#!/usr/bin/env python3
"""Which AI crawlers a site's robots.txt lets in, read the way RFC 9309 says a crawler reads it.

Usage:
    python3 aicrawlers.py example.com                   fetch https://example.com/robots.txt
    python3 aicrawlers.py https://example.com/shop      fetch the robots.txt of that host
    python3 aicrawlers.py --file public/robots.txt      read a local file, for example in a codebase
    python3 aicrawlers.py --stdin < robots.txt          read a pasted file
    Add --path /pricing --path /blog/post to test your own pages, and --json for machine output.

The crawler list, what each one does and the company's own documentation come from crawlers.json beside this
script (Visibian's AI crawler directory, each page read on the date it gives). The matching follows RFC 9309 and
Google's open-source robots.txt parser: the most specific group for a crawler wins, then the longest matching rule,
and Allow wins a tie. Apple documents that Applebot follows Googlebot's rules when no group names Applebot.

What this cannot see: a firewall, a CDN bot setting or a server rule that turns a crawler away by its user agent or
its address. Those block a crawler whatever robots.txt says.

Standard library only. It sends one request, identified as VisibianSkill/1.0, and follows up to five redirects.
"""
import argparse
import json
import pathlib
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
UA = "VisibianSkill/1.0 (+https://visibian.com)"
LIMIT = 500 * 1024          # RFC 9309 asks crawlers to read at least the first 500 KiB
TYPICAL = ["/", "/about", "/products/item-1234", "/2026/10/an-article.html"]
KIND = {"train": "training", "search": "search", "user": "user fetch", "archive": "archive"}


def load_crawlers():
    with open(HERE / "crawlers.json", encoding="utf-8") as f:
        return json.load(f)


# ------------------------------------------------------------------ parse and match

def parse(text):
    """The file's groups as [(agents, rules)]. A rule is (allow, path). Lines other than user-agent, allow and
    disallow (crawl-delay, sitemap) do not end a group, as in Google's parser."""
    groups, agents, rules, last = [], [], [], None
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip().lstrip("﻿")
        if ":" not in line:
            continue
        key, val = (s.strip() for s in line.split(":", 1))
        key = key.lower().replace(" ", "").replace("_", "-")
        if key in ("user-agent", "useragent"):
            if last == "rule":
                groups.append((agents, rules))
                agents, rules = [], []
            agents.append(val.split("/")[0].strip().lower())
            last = "agent"
        elif key in ("allow", "disallow") and agents:
            if val:
                rules.append((key == "allow", val))
            last = "rule"
    if agents:
        groups.append((agents, rules))
    return groups


def group_for(groups, token):
    """The rules a crawler with this product token follows, and which group gave them."""
    t = token.lower()
    chosen = [rules for agents, rules in groups if t in agents]
    source = token
    if not chosen and t == "applebot":
        chosen = [rules for agents, rules in groups if "googlebot" in agents]
        source = "Googlebot"
    if not chosen:
        chosen = [rules for agents, rules in groups if "*" in agents]
        source = "*"
    if not chosen:
        return None, None
    return [r for rules in chosen for r in rules], source


def _pattern(p):
    end = p.endswith("$")
    body = re.escape(p[:-1] if end else p).replace(r"\*", ".*")
    return re.compile(body + ("$" if end else ""))


def allowed(rules, path):
    if not rules or path == "/robots.txt":
        return True
    best = None   # (length, allow)
    for allow, p in rules:
        if _pattern(p).match(path):
            cand = (len(p), allow)
            if best is None or cand[0] > best[0] or (cand[0] == best[0] and allow):
                best = cand
    return True if best is None else best[1]


# ------------------------------------------------------------------ fetch

def robots_url(target):
    if "://" not in target:
        target = "https://" + target
    u = urllib.parse.urlsplit(target)
    return urllib.parse.urlunsplit((u.scheme or "https", u.netloc, "/robots.txt", "", ""))


def fetch(url):
    """(state, text, detail). state: rules, none (4xx: no restrictions), unreachable (5xx, 429 or no answer:
    RFC 9309 says to assume everything is disallowed), html (a web page served in place of the file)."""
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/plain,*/*;q=0.5"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            body = r.read(LIMIT).decode("utf-8", "replace")
            ctype = r.headers.get("Content-Type", "")
            head = body.lstrip()[:200].lower()
            if "html" in ctype.lower() or head.startswith(("<!doctype", "<html", "<head")):
                return "html", "", f"{r.status}, {ctype or 'no content type'}, a web page instead of a robots.txt file"
            return "rules", body, f"{r.status}, {r.geturl()}"
    except urllib.error.HTTPError as e:
        if e.code == 429 or e.code >= 500:
            return "unreachable", "", f"HTTP {e.code}"
        return "none", "", f"HTTP {e.code}"
    except Exception as e:  # DNS, TLS, timeout
        return "unreachable", "", f"{type(e).__name__}: {e}"


# ------------------------------------------------------------------ report

def evaluate(text, state, paths, crawlers):
    groups = parse(text) if state == "rules" else []
    rows = []
    for c in crawlers:
        if state == "unreachable":
            access, source = "closed (file unreachable)", None
            per_path = {p: False for p in paths}
        else:
            rules, source = group_for(groups, c["token"])
            per_path = {p: allowed(rules, p) for p in paths}
            shut = sum(not ok for ok in per_path.values())
            access = "closed" if shut == len(paths) else "limited" if shut else "open"
        rows.append({**c, "access": access, "group": source, "paths": per_path,
                     "named": any(c["token"].lower() in a for a, _ in groups)})
    return groups, rows


def warnings(state, groups, rows):
    out = []
    if state == "unreachable":
        out.append("The file could not be read (a server error, a rate limit or no answer). RFC 9309 tells crawlers "
                   "to treat that as a full block until it can be read again. Fix the server first.")
    if state == "html":
        out.append("The address answers with a web page, not a robots.txt file. Crawlers read that as no rules, "
                   "so nothing is blocked, but nothing is stated either. Serve a plain text file.")
    for r in rows:
        if r["kind"] in ("search", "user") and r["access"].startswith("closed"):
            out.append(f"{r['token']} is shut out. It is a {KIND[r['kind']]} crawler for {r['product']}: "
                       f"{r['blocking']}")
        elif r["kind"] in ("search", "user") and r["access"] == "limited":
            out.append(f"{r['token']} can read only some of the tested pages. Check that the closed paths are "
                       f"meant to be private.")
    star = [rules for agents, rules in groups if "*" in agents]
    if any((False, "/") in rules for rules in star):
        out.append("The group for every crawler (User-agent: *) disallows the whole site. Any crawler without a "
                   "group of its own is shut out, including new AI search crawlers.")
    return out


def render(target, state, detail, rows, notes, paths, read):
    lines = [f"robots.txt for {target}: {detail}", ""]
    lines.append("| Crawler | Company | Used for | Kind | Follows robots.txt | Tested pages | Rules from |")
    lines.append("|---|---|---|---|---|---|---|")
    for r in rows:
        lines.append(f"| {r['token']} | {r['company']} | {r['product']} | {KIND[r['kind']]} | {r['follows']} | "
                     f"{r['access']} | {r['group'] or 'no group'} |")
    lines.append("")
    lines.append("Tested pages: " + ", ".join(paths))
    if notes:
        lines.append("")
        lines.append("Points to look at:")
        lines += [f"- {n}" for n in notes]
    lines.append("")
    lines.append(f"Crawler facts from each company's own documentation, read {read}. Robots.txt is a request: "
                 f"crawlers that follow it obey it, and a firewall or CDN rule can still turn any crawler away.")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("target", nargs="?", help="a domain or URL whose robots.txt to fetch")
    ap.add_argument("--file", help="read a local robots.txt instead")
    ap.add_argument("--stdin", action="store_true", help="read robots.txt from standard input")
    ap.add_argument("--path", action="append", default=[], help="a path to test, such as /pricing (repeatable)")
    ap.add_argument("--json", action="store_true", help="print JSON")
    a = ap.parse_args(argv)

    data = load_crawlers()
    crawlers, read = data["crawlers"], data["read"]
    paths = a.path or TYPICAL

    if a.file:
        text = pathlib.Path(a.file).read_text(encoding="utf-8", errors="replace")[:LIMIT]
        state, detail, target = "rules", f"local file {a.file}", a.file
    elif a.stdin:
        text = sys.stdin.read()[:LIMIT]
        state, detail, target = "rules", "pasted file", "the pasted file"
    elif a.target:
        url = robots_url(a.target)
        state, text, detail = fetch(url)
        target = url
    else:
        ap.error("give a domain or URL, --file or --stdin")

    if state == "rules" and not parse(text):
        state = "none" if not text.strip() else state
    groups, rows = evaluate(text, state, paths, crawlers)
    notes = warnings(state, groups, rows)
    if a.json:
        print(json.dumps({"target": target, "state": state, "detail": detail, "read": read, "paths": paths,
                          "crawlers": rows, "notes": notes}, indent=2))
    else:
        print(render(target, state, detail, rows, notes, paths, read))
    return 0


if __name__ == "__main__":
    sys.exit(main())
