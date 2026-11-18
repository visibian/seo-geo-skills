#!/usr/bin/env python3
"""Outlines of the pages that already answer a topic, side by side, for writing a content brief.

Usage:
    python3 page_outline.py https://a.example/guide https://b.example/guide https://yoursite.com/guide
    python3 page_outline.py --file draft.html https://b.example/guide
    Add --json for machine output.

For each page: title, main heading, the H2 and H3 outline, words in the main text, headings written as questions,
lists and tables, links to sources, structured data and dates. Then the headings several pages share, which point to
what a reader of this topic expects. It fetches only the addresses given, once each. Standard library only;
page_check.py sits beside it.
"""
import argparse
import collections
import json
import pathlib
import re
import sys
import urllib.parse

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import page_check  # noqa: E402

STOP = set("""a an and are as at be by can do does for from how i if in is it of on or the to vs what when where which who
why with your you my our this that these those""".split())


def outline(doc, url=""):
    f = page_check.page_facts(doc)
    body = re.sub(r"<(script|style|noscript|template|svg|nav|header|footer|aside|form)\b.*?</\1>", " ", doc,
                  flags=re.S | re.I)
    main = re.search(r"<(main|article)\b.*?</\1>", body, re.S | re.I)
    main = main.group(0) if main else body
    heads = [(int(m.group(1)), page_check.text_of(m.group(2)))
             for m in re.finditer(r"<h([2-3])\b[^>]*>(.*?)</h\1>", main, re.S | re.I)]
    host = urllib.parse.urlsplit(url).netloc
    ext = [h for h in (page_check.attr(t, "href") or "" for t in re.findall(r"<a\b[^>]*>", main, re.I))
           if h.startswith("http") and urllib.parse.urlsplit(h).netloc not in ("", host)]
    return {"url": url, "title": f["title"], "h1": f["h1"], "outline": heads,
            "words": len(page_check.text_of(main).split()),
            "questions": [h for _, h in heads if h.rstrip().endswith("?")],
            "lists": len(re.findall(r"<(ul|ol)\b", main, re.I)), "tables": len(re.findall(r"<table\b", main, re.I)),
            "source_links": len(set(ext)), "jsonld_types": f["jsonld_types"], "dates": f["dates"]}


def key(h):
    return " ".join(sorted({w for w in re.findall(r"[a-z0-9]+", h.lower()) if w not in STOP and len(w) > 2}))


def shared(pages):
    seen = collections.defaultdict(set)
    label = {}
    for i, p in enumerate(pages):
        for lvl, h in p["outline"]:
            k = key(h)
            if k:
                seen[k].add(i)
                label.setdefault(k, h)
    return sorted(({"heading": label[k], "pages": len(v)} for k, v in seen.items() if len(v) >= 2),
                  key=lambda x: -x["pages"])


def render(pages, common):
    L = ["# Pages on this topic", ""]
    for p in pages:
        L += [f"## {p['title'] or p['url']}", f"{p['url']}", "",
              f"- Main heading: {' | '.join(p['h1']) or 'none'}",
              f"- Words in the main text: {p['words']}; lists: {p['lists']}; tables: {p['tables']}; "
              f"links to other sites: {p['source_links']}",
              f"- Structured data: {', '.join(p['jsonld_types']) or 'none'}; dates: "
              f"{', '.join(f'{k} {v}' for k, v in p['dates'].items()) or 'none'}", "", "Outline:"]
        L += [f"{'  ' * (lvl - 2)}- {h}" for lvl, h in p["outline"][:40]] or ["- no H2 or H3 headings"]
        L.append("")
    L += ["## Headings several pages share", ""]
    L += [f"- {c['heading']} ({c['pages']} pages)" for c in common[:30]] or ["- none"]
    L += ["", "Shared headings show what readers of this topic are used to finding. Cover what they need, then add "
              "what none of these pages has: first-hand data, a worked example, a clearer answer."]
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("urls", nargs="*")
    ap.add_argument("--file", action="append", default=[])
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if not a.urls and not a.file:
        ap.error("give one or more addresses or --file")
    pages = []
    for f in a.file:
        pages.append(outline(pathlib.Path(f).read_text(encoding="utf-8", errors="replace"), f))
    for u in a.urls:
        u = u if "://" in u else "https://" + u
        g = page_check.get(u)
        if g["status"] != 200:
            print(f"{u} answered {g['status'] or g.get('error')}; left out", file=sys.stderr)
            continue
        pages.append(outline(g["body"], g["url"]))
    common = shared(pages)
    print(json.dumps({"pages": pages, "shared_headings": common}, indent=1) if a.json else render(pages, common))
    return 0


if __name__ == "__main__":
    sys.exit(main())
