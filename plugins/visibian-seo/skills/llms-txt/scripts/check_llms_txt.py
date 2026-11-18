#!/usr/bin/env python3
"""Check an llms.txt file against the format at llmstxt.org (v2).

Usage:
    python3 check_llms_txt.py example.com            fetch https://example.com/llms.txt
    python3 check_llms_txt.py https://example.com/docs/llms.txt
    python3 check_llms_txt.py --file public/llms.txt
    Add --links to also request every linked URL once and report the ones that do not open.

The format: an H1 with the site's name (the only required part), then an optional blockquote summary, then optional
text without headings, then H2 sections that each hold a list of links written as "- [name](url)" with optional
": notes". A section named "Optional" holds links an agent can skip.

Standard library only.
"""
import argparse
import pathlib
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

UA = "VisibianSkill/1.0 (+https://visibian.com)"
LINK = re.compile(r"^\s*[-*+]\s+\[([^\]]+)\]\(([^)\s]+)\)\s*(?::\s*(.*))?$")


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.status, r.headers.get("Content-Type", ""), r.read(2 * 1024 * 1024).decode("utf-8", "replace")


def check(text, base=None):
    errors, warnings, notes = [], [], []
    lines = text.lstrip("﻿").splitlines()
    body = [l for l in lines if l.strip()]
    if not body:
        return ["the file is empty"], [], [], []
    if not body[0].startswith("# "):
        errors.append("the first line must be an H1 with the site's name, such as '# Example Co'")
    if sum(1 for l in lines if re.match(r"^#\s", l)) > 1:
        errors.append("there is more than one H1")
    if len(body) > 1 and not body[1].startswith(">"):
        notes.append("no blockquote summary after the H1; the format recommends one short summary line")
    section, links, seen_h2 = None, [], False
    for n, line in enumerate(lines, 1):
        if re.match(r"^###+\s", line):
            errors.append(f"line {n}: only H1 and H2 headings belong in the file")
        elif line.startswith("## "):
            section, seen_h2 = line[3:].strip(), True
        elif seen_h2 and line.strip() and not line.startswith(">"):
            m = LINK.match(line)
            if m:
                name, url, note = m.groups()
                full = urllib.parse.urljoin(base, url) if base else url
                links.append((section, name, full))
                if not re.match(r"^https?://", full):
                    warnings.append(f"line {n}: link is relative ({url}); use a full URL so it works out of context")
            elif re.match(r"^\s*[-*+]\s", line):
                errors.append(f"line {n}: a list item in a section must start with a markdown link [name](url)")
    if not links:
        notes.append("no link lists; the file is valid, but agents get most from links to the key pages")
    if any(s and s.lower() == "optional" for s, _, _ in links):
        notes.append("an 'Optional' section is present: agents may skip its links when space is short")
    if len(text) > 50_000:
        warnings.append(f"the file is {len(text):,} characters; keep it small enough to fit in an agent's context")
    return errors, warnings, notes, links


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("target", nargs="?")
    ap.add_argument("--file")
    ap.add_argument("--links", action="store_true", help="request each linked URL once")
    a = ap.parse_args(argv)
    base = None
    if a.file:
        text = pathlib.Path(a.file).read_text(encoding="utf-8", errors="replace")
        where = a.file
    elif a.target:
        url = a.target if "://" in a.target else f"https://{a.target}"
        if not urllib.parse.urlsplit(url).path.endswith("llms.txt"):
            url = urllib.parse.urljoin(url if url.endswith("/") else url + "/", "/llms.txt")
        try:
            status, ctype, text = fetch(url)
        except urllib.error.HTTPError as e:
            e.close()
            print(f"{url}: HTTP {e.code}. There is no llms.txt at this address.")
            return 0
        except Exception as e:
            print(f"{url}: could not be fetched ({type(e).__name__}: {e}).")
            return 0
        where, base = f"{url} ({status}, {ctype or 'no content type'})", url
        if "html" in ctype.lower() or text.lstrip()[:15].lower().startswith(("<!doctype", "<html")):
            print(f"{where}: the address answers with a web page, not a markdown file.")
            return 0
    else:
        ap.error("give a domain or URL, or --file")
    errors, warnings, notes, links = check(text, base)
    print(f"{where}: {len(links)} link(s) in {len({s for s, _, _ in links})} section(s)")
    for e in errors:
        print(f"ERROR    {e}")
    for w in warnings:
        print(f"WARNING  {w}")
    for n in notes:
        print(f"NOTE     {n}")
    if a.links:
        for section, name, url in links:
            if not url.startswith("http"):
                continue
            try:
                status, _, _ = fetch(url)
                if status >= 400:
                    print(f"BROKEN   {url} ({status})")
            except urllib.error.HTTPError as e:
                e.close()
                print(f"BROKEN   {url} ({e.code})")
            except Exception as e:
                print(f"BROKEN   {url} ({type(e).__name__})")
    if not errors:
        print("The file follows the llms.txt format.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
