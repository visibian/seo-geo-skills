#!/usr/bin/env python3
"""Internal links from a site audit: orphans, deep pages, weakly linked pages, anchor text, and links worth adding.

Usage:
    python3 link_graph.py seo-audit/audit.json            read the audit the seo-audit skill wrote (site_audit.py --out)
    python3 link_graph.py seo-audit/audit.json --page https://example.com/pricing     one page in detail
    Add --json for machine output, --suggest 5 for how many link ideas per weak page (default 3).

Link ideas are pages that share words in their title and main heading with the weak page and do not link to it yet.
They are candidates for a person to judge, not a ranking. Standard library only.
"""
import argparse
import collections
import json
import re
import sys

STOP = set("""a an and are as at be but by for from has have how i if in into is it its of on or our so than that the
their them then there these they this to was we what when where which who why will with you your vs versus best guide
page home""".split())


def words(text):
    return {w for w in re.findall(r"[a-z0-9][a-z0-9'-]{2,}", (text or "").lower()) if w not in STOP}


def topic(p):
    return words(" ".join([p.get("title") or ""] + (p.get("h1") or [])))


def analyse(audit, per_page=3):
    pages = {u: p for u, p in audit["pages"].items() if "title" in p and p.get("status") == 200}
    inl = {u: audit["inlinks"].get(u, []) for u in pages}
    start = next(iter(audit["pages"]), None)
    linked_from = collections.defaultdict(set)
    for u, p in pages.items():
        for h, _, _ in p.get("internal_links", []):
            linked_from[h].add(u)
    sitemap = set(audit.get("sitemap_urls", []))
    orphans = sorted(u for u in pages if u != start and not inl[u] and u in sitemap)
    weak = sorted((u for u in pages if u != start and 0 < len({s for s, _ in inl[u]}) <= 1),
                  key=lambda u: len(inl[u]))
    deep = sorted((u for u in pages if (pages[u].get("depth") or 0) > 3), key=lambda u: -(pages[u].get("depth") or 0))
    anchors = {u: collections.Counter(a for _, a in inl[u] if a) for u in pages}
    topics = {u: topic(p) for u, p in pages.items()}
    suggestions = {}
    for u in orphans + weak + deep:
        if u in suggestions or not topics[u]:
            continue
        cands = []
        for v, p in pages.items():
            if v == u or v in linked_from[u] and u in {h for h, _, _ in p.get("internal_links", [])}:
                continue
            if u in {h for h, _, _ in p.get("internal_links", [])}:
                continue
            shared = topics[u] & topics[v]
            if shared:
                cands.append((len(shared) / len(topics[u] | topics[v]), v, sorted(shared)))
        cands.sort(reverse=True)
        suggestions[u] = [{"from": v, "shared_words": s} for _, v, s in cands[:per_page]]
    hubs = sorted(pages, key=lambda u: -len(inl[u]))[:10]
    return {
        "pages": len(pages),
        "orphans": orphans,
        "weak": weak,
        "deep": deep,
        "hubs": [{"url": u, "inlinks": len(inl[u]), "from_pages": len({s for s, _ in inl[u]})} for u in hubs],
        "anchors": {u: anchors[u].most_common(8) for u in pages},
        "suggestions": suggestions,
    }


def page_detail(audit, url):
    p = audit["pages"].get(url)
    if not p:
        return f"{url} is not in the audit."
    ins = audit["inlinks"].get(url, [])
    L = [f"# Internal links: {url}", "",
         f"- Click depth from the start page: {p.get('depth')}",
         f"- Links in: {len(ins)}, from {len({s for s, _ in ins})} pages",
         f"- Links out to the site: {len(p.get('internal_links', []))}", "", "## Anchors used to link here", ""]
    for a, n in collections.Counter(a for _, a in ins).most_common(15):
        L.append(f"- \"{a}\" x{n}")
    L += ["", "## Pages linking here", ""] + [f"- {s}" for s in sorted({s for s, _ in ins})[:40]]
    return "\n".join(L)


def render(r, n_show=15):
    L = [f"# Internal links: {r['pages']} pages read", ""]
    sec = [("Orphan pages", "in the sitemap, linked from no crawled page", r["orphans"]),
           ("Weakly linked pages", "linked from one page only", r["weak"]),
           ("Deep pages", "more than 3 clicks from the start page", r["deep"])]
    for title, what, urls in sec:
        L += [f"## {title} ({len(urls)}): {what}", ""]
        for u in urls[:n_show]:
            ideas = r["suggestions"].get(u) or []
            L.append(f"- {u}")
            for i in ideas:
                L.append(f"  - could be linked from {i['from']} (shared words: {', '.join(i['shared_words'][:6])})")
        if len(urls) > n_show:
            L.append(f"- and {len(urls) - n_show} more (see --json)")
        L.append("")
    L += ["## Most linked pages", ""] + [f"- {h['url']}: {h['inlinks']} links from {h['from_pages']} pages"
                                         for h in r["hubs"]]
    generic = {u: a for u, a in r["anchors"].items()
               if any(x.lower() in ("click here", "here", "read more", "more", "learn more") for x, _ in a)}
    if generic:
        L += ["", f"## Pages reached through generic anchors ({len(generic)})", ""]
        L += [f"- {u}: " + ", ".join(f"\"{x}\" x{n}" for x, n in a) for u, a in list(generic.items())[:n_show]]
    L += ["", "Link ideas come from shared words in titles and main headings; judge each by whether a reader of the "
              "source page would want the target page."]
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("audit")
    ap.add_argument("--page")
    ap.add_argument("--suggest", type=int, default=3)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    with open(a.audit, encoding="utf-8") as f:
        audit = json.load(f)
    if a.page:
        print(page_detail(audit, a.page))
        return 0
    r = analyse(audit, a.suggest)
    print(json.dumps(r, indent=1) if a.json else render(r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
