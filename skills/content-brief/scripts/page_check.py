#!/usr/bin/env python3
"""What a crawler that runs no scripts can read on one page, and the site files around it.

Usage:
    python3 page_check.py https://example.com/pricing        a live page, plus its site's robots.txt, sitemap, llms.txt
    python3 page_check.py --file out/pricing/index.html       a built page in a codebase (page facts only)
    Add --json for machine output, --no-site to skip the site files.

It reports what it observed: the answer code, indexing rules, title, description, canonical link, headings, how many
words of text are in the HTML before any script runs, signs that the text is added by scripts, structured data types,
dates, and, for a live page, which AI crawlers robots.txt lets read this path. It gives no score.

Standard library only. aicrawlers.py and crawlers.json must sit beside it.
"""
import argparse
import html
import json
import pathlib
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import aicrawlers  # noqa: E402

UA = aicrawlers.UA


def get(url, limit=3 * 1024 * 1024):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*;q=0.5"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return {"status": r.status, "url": r.geturl(), "headers": dict(r.headers),
                    "body": r.read(limit).decode("utf-8", "replace")}
    except urllib.error.HTTPError as e:
        return {"status": e.code, "url": url, "headers": dict(e.headers or {}), "body": ""}
    except Exception as e:
        return {"status": 0, "url": url, "headers": {}, "body": "", "error": f"{type(e).__name__}: {e}"}


def text_of(fragment):
    text = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()
    return re.sub(r"\s+([.,;:?])(?=\s|$)", r"\1", text)


def attr(tag, name):
    m = re.search(rf'\b{name}\s*=\s*("([^"]*)"|\'([^\']*)\'|([^\s>]+))', tag, re.I)
    return html.unescape(next(g for g in m.groups()[1:] if g is not None)) if m else None


def metas(doc):
    out = {}
    for tag in re.findall(r"<meta\b[^>]*>", doc, re.I):
        key = (attr(tag, "name") or attr(tag, "property") or "").lower()
        if key:
            out.setdefault(key, attr(tag, "content") or "")
    return out


def page_facts(doc, headers=None):
    headers = {k.lower(): v for k, v in (headers or {}).items()}
    head = re.search(r"<head\b.*?</head>", doc, re.S | re.I)
    head = head.group(0) if head else doc[:20000]
    m = metas(doc)
    title = re.search(r"<title[^>]*>(.*?)</title>", head, re.S | re.I)
    canon = next((attr(t, "href") for t in re.findall(r"<link\b[^>]*>", head, re.I)
                  if (attr(t, "rel") or "").lower() == "canonical"), None)
    md_alt = [attr(t, "href") for t in re.findall(r"<link\b[^>]*>", head, re.I)
              if (attr(t, "type") or "").lower() == "text/markdown"]
    lang = attr(re.search(r"<html\b[^>]*>", doc, re.I).group(0), "lang") if re.search(r"<html\b", doc, re.I) else None
    body = re.sub(r"<(script|style|noscript|template|svg)[^>]*>.*?</\1>", " ", doc, flags=re.S | re.I)
    visible = text_of(re.sub(r"<head\b.*?</head>", " ", body, flags=re.S | re.I))
    h1 = [text_of(x) for x in re.findall(r"<h1\b[^>]*>(.*?)</h1>", doc, re.S | re.I)]
    h2 = [text_of(x) for x in re.findall(r"<h2\b[^>]*>(.*?)</h2>", doc, re.S | re.I)]
    scripts = len(re.findall(r"<script\b", doc, re.I))
    app_root = bool(re.search(r'<div[^>]+id=["\'](root|app|__next|__nuxt|svelte)["\'][^>]*>\s*</div>', doc, re.I))
    ld = re.findall(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', doc, re.S | re.I)
    types, ld_errors, dates = [], 0, {}
    for raw in ld:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            ld_errors += 1
            continue
        stack = [data]
        while stack:
            x = stack.pop()
            if isinstance(x, dict):
                t = x.get("@type")
                types += [t] if isinstance(t, str) else [y for y in (t or []) if isinstance(y, str)]
                for k in ("datePublished", "dateModified"):
                    if isinstance(x.get(k), str):
                        dates.setdefault(k, x[k])
                stack += list(x.values())
            elif isinstance(x, list):
                stack += x
    for k in ("article:published_time", "article:modified_time"):
        if m.get(k):
            dates.setdefault(k, m[k])
    robots_meta = ", ".join(v for k, v in m.items() if k in ("robots", "googlebot", "bingbot")) or None
    return {
        "title": text_of(title.group(1)) if title else None,
        "description": m.get("description"),
        "canonical": canon,
        "lang": lang,
        "robots_meta": robots_meta,
        "x_robots_tag": headers.get("x-robots-tag"),
        "h1": h1,
        "h2_count": len(h2),
        "words": len(visible.split()),
        "scripts": scripts,
        "empty_app_root": app_root,
        "jsonld_types": sorted(set(types)),
        "jsonld_errors": ld_errors,
        "dates": dates,
        "og_title": m.get("og:title"),
        "markdown_alternate": md_alt,
    }


def findings(f, status=None, crawler_rows=None):
    """(level, message): blocker, fix, suggestion. Observed facts only."""
    out = []
    if status is not None and status != 200:
        out.append(("blocker" if status >= 400 or status == 0 else "fix", f"the page answered {status or 'nothing'}"))
    for src in (f["robots_meta"], f["x_robots_tag"]):
        if src and "noindex" in src.lower():
            out.append(("blocker", f"the page asks not to be indexed ({src}); search engines and their AI answers "
                                   f"will leave it out"))
        if src and ("nosnippet" in src.lower() or "max-snippet:0" in src.replace(" ", "").lower()):
            out.append(("fix", f"snippets are switched off ({src}); Google uses these rules for its AI features too"))
    if f["words"] < 80:
        hint = " The page has an empty app root, so its text is likely added by scripts." if f["empty_app_root"] else ""
        out.append(("blocker", f"only {f['words']} words of text in the HTML before scripts run.{hint} Crawlers that "
                               f"do not run scripts, and assistants that read the raw page, see little or nothing."))
    elif f["words"] < 250 and f["scripts"] > 15:
        out.append(("fix", f"{f['words']} words in the raw HTML with {f['scripts']} scripts; check that the main "
                           f"text is in the HTML and not added after load"))
    if not f["title"]:
        out.append(("fix", "no <title>"))
    if not f["description"]:
        out.append(("fix", "no meta description"))
    if len(f["h1"]) != 1:
        out.append(("fix", f"{len(f['h1'])} <h1> headings; use exactly one that says what the page is"))
    if not f["canonical"]:
        out.append(("suggestion", "no canonical link"))
    if not f["lang"]:
        out.append(("suggestion", "no lang attribute on <html>"))
    if f["jsonld_errors"]:
        out.append(("fix", f"{f['jsonld_errors']} JSON-LD block(s) are not valid JSON"))
    if not f["jsonld_types"]:
        out.append(("suggestion", "no structured data; see the structured-data skill"))
    if not f["dates"]:
        out.append(("suggestion", "no published or updated date in the markup; show the date on pages where it "
                                  "matters, such as articles and price lists"))
    for r in crawler_rows or []:
        if r["kind"] in ("search", "user") and r["paths"] and not all(r["paths"].values()):
            out.append(("blocker", f"robots.txt closes this page to {r['token']} ({r['product']})"))
    return out


def site_files(page_url, path):
    host = urllib.parse.urlsplit(page_url)
    root = f"{host.scheme}://{host.netloc}"
    state, text, detail = aicrawlers.fetch(root + "/robots.txt")
    data = aicrawlers.load_crawlers()
    groups, rows = aicrawlers.evaluate(text, state, [path], data["crawlers"])
    sitemaps = re.findall(r"(?im)^\s*sitemap\s*:\s*(\S+)", text) if state == "rules" else []
    sm = sitemaps[0] if sitemaps else root + "/sitemap.xml"
    sm_get = get(sm, limit=200_000)
    llms = get(root + "/llms.txt", limit=200_000)
    llms_ok = llms["status"] == 200 and not llms["body"].lstrip()[:15].lower().startswith(("<!doctype", "<html"))
    return {
        "robots": {"state": state, "detail": detail, "read": data["read"]},
        "crawlers": rows,
        "sitemap": {"url": sm, "declared": bool(sitemaps), "status": sm_get["status"]},
        "llms_txt": {"present": llms_ok, "status": llms["status"]},
    }


def render(target, status, f, site, notes):
    L = [f"# What a crawler reads on {target}", ""]
    if status is not None:
        L.append(f"- Answer: {status}")
    L += [f"- Title: {f['title'] or 'none'}",
          f"- Description: {f['description'] or 'none'}",
          f"- Canonical: {f['canonical'] or 'none'}",
          f"- Language: {f['lang'] or 'not set'}",
          f"- Indexing rules: {f['robots_meta'] or 'none in the page'}; header: {f['x_robots_tag'] or 'none'}",
          f"- H1: {' | '.join(f['h1']) or 'none'}; H2 headings: {f['h2_count']}",
          f"- Words in the HTML before scripts run: {f['words']} (scripts on the page: {f['scripts']})",
          f"- Structured data: {', '.join(f['jsonld_types']) or 'none'}",
          f"- Dates: {', '.join(f'{k} {v}' for k, v in f['dates'].items()) or 'none found'}"]
    if site:
        ok = [r["token"] for r in site["crawlers"] if all(r["paths"].values())]
        shut = [r["token"] for r in site["crawlers"] if not all(r["paths"].values())]
        L += ["", "## Site files",
              f"- robots.txt: {site['robots']['detail']}",
              f"- AI crawlers allowed on this page: {', '.join(ok) or 'none'}",
              f"- AI crawlers closed on this page: {', '.join(shut) or 'none'}",
              f"- Sitemap: {site['sitemap']['url']} answered {site['sitemap']['status']}"
              f"{'' if site['sitemap']['declared'] else ' (not declared in robots.txt)'}",
              f"- llms.txt: {'present' if site['llms_txt']['present'] else 'not found'}"]
    L += ["", "## Findings"]
    order = {"blocker": 0, "fix": 1, "suggestion": 2}
    L += [f"- **{lvl}**: {msg}" for lvl, msg in sorted(notes, key=lambda n: order[n[0]])] or ["- nothing found"]
    L += ["", "Observed from the raw HTML, without running scripts. A browser, or a crawler that runs scripts, may "
              "see more. Firewall and CDN rules are not visible from here."]
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("url", nargs="?")
    ap.add_argument("--file")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-site", action="store_true")
    a = ap.parse_args(argv)
    if a.file:
        doc = pathlib.Path(a.file).read_text(encoding="utf-8", errors="replace")
        f, status, site, target = page_facts(doc), None, None, a.file
    elif a.url:
        url = a.url if "://" in a.url else "https://" + a.url
        r = get(url)
        f, status, target = page_facts(r["body"], r["headers"]), r["status"], r["url"]
        path = urllib.parse.urlsplit(r["url"]).path or "/"
        site = None if a.no_site else site_files(r["url"], path)
    else:
        ap.error("give a URL or --file")
    notes = findings(f, status, site["crawlers"] if site else None)
    if a.json:
        print(json.dumps({"target": target, "status": status, "page": f, "site": site,
                          "findings": [{"level": l, "message": m} for l, m in notes]}, indent=2, default=str))
    else:
        print(render(target, status, f, site, notes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
