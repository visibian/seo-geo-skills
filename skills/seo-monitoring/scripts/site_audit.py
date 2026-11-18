#!/usr/bin/env python3
"""Crawl a website the way a search crawler does, and report what is broken, missing or inconsistent.

Usage:
    python3 site_audit.py https://example.com                     up to 100 pages, from the home page and the sitemap
    python3 site_audit.py https://example.com --max-pages 300 --out audit/
                                                                  also writes audit/report.md and audit/audit.json
    --json            print the full data instead (internal-linking, hreflang and seo-report read it)
    --delay 0.5       seconds between requests (the default); --no-sitemap to follow links only

It reports observed facts, never a score: answer codes and redirect chains, titles and descriptions, headings,
canonical links, indexing rules, language and hreflang tags, words in the HTML before scripts run, images without alt
text, structured data, internal links and their anchors, click depth, the sitemap against what the links reach,
robots.txt for search and AI crawlers, and llms.txt.

It reads robots.txt first and skips what robots.txt closes to it. It identifies itself as VisibianSkill/1.0.
Standard library only; page_check.py, aicrawlers.py and crawlers.json sit beside it.
"""
import argparse
import collections
import gzip
import json
import pathlib
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
import xml.etree.ElementTree as ET

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import aicrawlers  # noqa: E402
import page_check  # noqa: E402

UA = aicrawlers.UA
TOKEN = "VisibianSkill"
SKIP_PATH = re.compile(r"^/cdn-cgi/")   # Cloudflare's own addresses (email protection and the like)
SKIP_EXT = re.compile(r"\.(pdf|jpe?g|png|gif|webp|avif|svg|ico|css|js|mjs|json|xml|txt|zip|gz|mp4|webm|mp3|wav|woff2?|ttf|"
                      r"otf|eot|docx?|xlsx?|pptx?|csv|rss|atom)$", re.I)
GENERIC_ANCHORS = {"click here", "here", "read more", "more", "learn more", "this", "link", "this page", "continue"}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None   # redirects are followed by hand, so every hop is recorded


OPENER = urllib.request.build_opener(NoRedirect)


def fetch(url, limit=3 * 1024 * 1024, hops=10):
    """GET with every redirect recorded: {status, url (final), chain [(code, url)], headers, body, error}."""
    chain, current = [], url
    for _ in range(hops + 1):
        req = urllib.request.Request(current, headers={"User-Agent": UA, "Accept": "text/html,*/*;q=0.5"})
        try:
            with OPENER.open(req, timeout=25) as r:
                ctype = r.headers.get("Content-Type", "")
                body = r.read(limit) if ("html" in ctype or "xml" in ctype or not ctype) else b""
                if body[:2] == b"\x1f\x8b":
                    body = gzip.decompress(body)
                return {"status": r.status, "url": current, "chain": chain, "headers": dict(r.headers),
                        "ctype": ctype, "body": body.decode("utf-8", "replace")}
        except urllib.error.HTTPError as e:
            if 300 <= e.code < 400 and e.headers.get("Location"):
                nxt = urllib.parse.urljoin(current, e.headers["Location"])
                chain.append((e.code, nxt))
                if nxt in [current] + [u for _, u in chain[:-1]]:
                    return {"status": e.code, "url": nxt, "chain": chain, "headers": dict(e.headers), "ctype": "",
                            "body": "", "error": "redirect loop"}
                current = nxt
                continue
            return {"status": e.code, "url": current, "chain": chain, "headers": dict(e.headers or {}), "ctype": "",
                    "body": ""}
        except Exception as e:  # network errors, timeouts, bad certificates
            return {"status": 0, "url": current, "chain": chain, "headers": {}, "ctype": "", "body": "",
                    "error": f"{type(e).__name__}: {e}"}
    return {"status": 0, "url": current, "chain": chain, "headers": {}, "ctype": "", "body": "",
            "error": f"more than {hops} redirects"}


def norm(url, base=None):
    """Absolute URL without fragment, lower-case scheme and host, no default port."""
    url = urllib.parse.urljoin(base, url) if base else url
    p = urllib.parse.urlsplit(url.strip())
    if p.scheme not in ("http", "https"):
        return None
    host = (p.hostname or "").lower()
    port = f":{p.port}" if p.port and p.port not in (80, 443) else ""
    return urllib.parse.urlunsplit((p.scheme.lower(), host + port, p.path or "/", p.query, ""))


def links_of(doc, base):
    """(href, anchor text, rel) for every <a href>."""
    out = []
    for m in re.finditer(r"<a\b([^>]*)>(.*?)</a>", doc, re.S | re.I):
        tag = "<a " + m.group(1) + ">"
        href = page_check.attr(tag, "href")
        if not href or href.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
            continue
        anchor = page_check.text_of(m.group(2))
        if not anchor:
            img = re.search(r"<img\b[^>]*>", m.group(2), re.I)
            anchor = f"[image: {page_check.attr(img.group(0), 'alt') or 'no alt'}]" if img else ""
        out.append((norm(href, base), anchor, (page_check.attr(tag, "rel") or "").lower()))
    return [o for o in out if o[0]]


def extra_facts(doc, url):
    # images a reader sees: not tracking pixels (inside <noscript>, or 1 by 1)
    seen = re.sub(r"<noscript\b.*?</noscript>", " ", doc, flags=re.S | re.I)
    imgs = [t for t in re.findall(r"<img\b[^>]*>", seen, re.I)
            if not (page_check.attr(t, "width") == "1" and page_check.attr(t, "height") == "1")]
    no_alt = sum(1 for t in imgs if page_check.attr(t, "alt") is None)
    head = re.search(r"<head\b.*?</head>", doc, re.S | re.I)
    head = head.group(0) if head else doc[:20000]
    hreflang = [((page_check.attr(t, "hreflang") or "").strip(), norm(page_check.attr(t, "href") or "", url))
                for t in re.findall(r"<link\b[^>]*>", head, re.I)
                if (page_check.attr(t, "rel") or "").lower() == "alternate" and page_check.attr(t, "hreflang")]
    mixed = 0
    if url.startswith("https://"):
        for t in re.findall(r"<(?:img|script|iframe|source|video|audio)\b[^>]*>|<link\b[^>]*stylesheet[^>]*>", doc, re.I):
            src = page_check.attr(t, "src") or page_check.attr(t, "href") or ""
            mixed += src.startswith("http://")
    m = page_check.metas(doc)
    return {"images": len(imgs), "images_no_alt": no_alt, "hreflang": hreflang, "mixed_content": mixed,
            "viewport": "viewport" in m, "og_image": bool(m.get("og:image"))}


def read_sitemaps(start_url, robots_text, cap=5000):
    root = "{0.scheme}://{0.netloc}".format(urllib.parse.urlsplit(start_url))
    queue = re.findall(r"(?im)^\s*sitemap\s*:\s*(\S+)", robots_text or "") or [root + "/sitemap.xml"]
    declared = bool(re.findall(r"(?im)^\s*sitemap\s*:", robots_text or ""))
    seen, urls, notes = set(), [], []
    while queue and len(seen) < 25 and len(urls) < cap:
        sm = queue.pop(0)
        if sm in seen:
            continue
        seen.add(sm)
        r = fetch(sm, limit=20 * 1024 * 1024)
        if r["status"] != 200:
            notes.append(f"{sm} answered {r['status'] or r.get('error')}")
            continue
        try:
            tree = ET.fromstring(r["body"].encode("utf-8"))
        except ET.ParseError as e:
            notes.append(f"{sm} is not valid XML ({e})")
            continue
        tag = tree.tag.split("}")[-1]
        locs = [e.text.strip() for e in tree.iter() if e.tag.split("}")[-1] == "loc" and e.text]
        if tag == "sitemapindex":
            queue += locs
        else:
            urls += locs
    return {"declared": declared, "files": sorted(seen), "urls": urls[:cap], "notes": notes}


def crawl(start, max_pages=100, delay=0.5, use_sitemap=True, log=None):
    first = fetch(start)
    start_final = norm(first["url"]) or start
    site = urllib.parse.urlsplit(start_final).netloc
    root = f"{urllib.parse.urlsplit(start_final).scheme}://{site}"
    state, robots_text, robots_detail = aicrawlers.fetch(root + "/robots.txt")
    rp = urllib.robotparser.RobotFileParser()
    rp.parse((robots_text or "").splitlines() if state == "rules" else [])
    sitemap = read_sitemaps(start_final, robots_text if state == "rules" else "") if use_sitemap else \
        {"declared": False, "files": [], "urls": [], "notes": ["not read (--no-sitemap)"]}
    in_sitemap = {norm(u) for u in sitemap["urls"] if norm(u)}

    pages, depth, inlinks, skipped = {}, {start_final: 0}, collections.defaultdict(list), []
    queue = collections.deque([start_final])
    queued = {start_final}
    extra = [u for u in sorted(in_sitemap) if urllib.parse.urlsplit(u).netloc == site]
    while (queue or extra) and len(pages) < max_pages:
        url = queue.popleft() if queue else extra.pop(0)
        if url in pages:
            continue
        if not rp.can_fetch(TOKEN, url):
            skipped.append(url)
            pages[url] = {"url": url, "status": None, "robots_blocked": True}
            continue
        reuse = url == start_final and first["status"] and not first["chain"]
        r = first if reuse else fetch(url)
        if not reuse:
            time.sleep(delay)
        rec = {"url": url, "final_url": norm(r["url"]), "status": r["status"], "chain": r["chain"],
               "error": r.get("error"), "ctype": r["ctype"], "depth": depth.get(url), "in_sitemap": url in in_sitemap}
        if r["status"] == 200 and "html" in (r["ctype"] or "html") and r["body"]:
            facts = page_check.page_facts(r["body"], r["headers"])
            base = r["url"]
            links = links_of(r["body"], base)
            internal = [(h, a, rel) for h, a, rel in links if urllib.parse.urlsplit(h).netloc == site]
            rec.update(facts)
            rec.update(extra_facts(r["body"], r["url"]))
            rec["internal_links"] = internal
            rec["external_links"] = sum(1 for h, _, _ in links if urllib.parse.urlsplit(h).netloc != site)
            rec["canonical_abs"] = norm(facts["canonical"], base) if facts["canonical"] else None
            for h, a, rel in internal:
                inlinks[h].append((url, a))
                path = urllib.parse.urlsplit(h).path
                if h not in queued and not SKIP_EXT.search(path) and not SKIP_PATH.search(path):
                    queued.add(h)
                    depth.setdefault(h, (depth.get(url) or 0) + 1)
                    queue.append(h)
        pages[url] = rec
        if log:
            log(f"{len(pages):>4} {r['status']} {url}")
        if r["chain"] and r["status"] == 200:
            fin = norm(r["url"])
            if fin and urllib.parse.urlsplit(fin).netloc == site and fin not in queued:
                queued.add(fin)
                depth.setdefault(fin, depth.get(url))
                queue.append(fin)

    data = aicrawlers.load_crawlers()
    _, rows = aicrawlers.evaluate(robots_text, state, ["/"], data["crawlers"])
    llms = fetch(root + "/llms.txt", limit=300_000)
    llms_ok = llms["status"] == 200 and not llms["body"].lstrip()[:15].lower().startswith(("<!doctype", "<html"))
    for p in pages.values():
        p["inlinks"] = len(inlinks.get(p["url"], []))
        p["depth"] = depth.get(p["url"], p.get("depth"))
    not_crawled = sorted(h for h in inlinks if h not in pages and not SKIP_EXT.search(urllib.parse.urlsplit(h).path)
                         and not SKIP_PATH.search(urllib.parse.urlsplit(h).path))
    return {
        "start": start, "site": root, "checked": time.strftime("%Y-%m-%d"), "max_pages": max_pages,
        "robots": {"state": state, "detail": robots_detail, "skipped_for_this_script": skipped},
        "crawlers": rows, "crawler_facts_read": data["read"],
        "sitemap": {k: sitemap[k] for k in ("declared", "files", "notes")} | {"count": len(in_sitemap)},
        "llms_txt": llms_ok,
        "pages": pages,
        "inlinks": {k: v for k, v in inlinks.items()},
        "not_crawled": not_crawled,
        "sitemap_urls": sorted(in_sitemap),
    }


# ------------------------------------------------------------------ findings

def n(count, one, many=None):
    """1 page, 2 pages."""
    return f"{count} {one if count == 1 else (many or one + 's')}"


def indexable(p):
    rules = " ".join(filter(None, [p.get("robots_meta"), p.get("x_robots_tag")])).lower()
    canon_ok = not p.get("canonical_abs") or p["canonical_abs"] == p["url"] or p["canonical_abs"] == p.get("final_url")
    return p.get("status") == 200 and "noindex" not in rules and canon_ok and "title" in p


def true_duplicates(groups, pages):
    """Pages in a group with another page that is not its hreflang alternate (regional editions may share a title)."""
    alts = {u: {h for _, h in pages[u].get("hreflang", [])} for v in groups.values() for u in v}
    out = []
    for v in groups.values():
        for u in v:
            if any(w != u and w not in alts[u] and u not in alts.get(w, set()) for w in v):
                out.append(u)
    return out


def findings(a):
    """[(level, category, message, [urls])], levels blocker, fix, suggestion."""
    out, pages = [], a["pages"]
    html_pages = [p for p in pages.values() if "title" in p]
    idx = [p for p in html_pages if indexable(p)]
    add = lambda lvl, cat, msg, urls: out.append((lvl, cat, msg, sorted(set(urls))))

    start = pages.get(next(iter(pages), ""), {})
    if start and start.get("status") != 200:
        add("blocker", "Crawling", f"the start page answered {start.get('status') or start.get('error')}", [start["url"]])
    shut = [r for r in a["crawlers"] if r["kind"] == "search" and r["paths"] and not all(r["paths"].values())]
    if shut:
        add("blocker", "Crawling", "robots.txt closes the home page to search crawlers: " +
            ", ".join(f"{r['token']} ({r['product']})" for r in shut), [a["site"] + "/robots.txt"])
    if a["robots"]["skipped_for_this_script"]:
        add("suggestion", "Crawling", "robots.txt closes some pages to every crawler, so they were not checked",
            a["robots"]["skipped_for_this_script"])

    broken = collections.defaultdict(list)
    for target, srcs in a["inlinks"].items():
        t = pages.get(target)
        if t and t.get("status") is not None and (t["status"] == 0 or t["status"] >= 400):
            broken[target] += [s for s, _ in srcs]
    if broken:
        add("fix", "Links", f"{n(len(broken), 'linked page')} answer{'s' if len(broken) == 1 else ''} an error, linked from "
            f"{n(len({s for v in broken.values() for s in v}), 'page')}", list(broken))
    redirected = [u for u in a["inlinks"] if pages.get(u, {}).get("chain")]
    if redirected:
        add("fix", "Links", f"internal links point at {n(len(redirected), 'address', 'addresses')} that redirect; link to the final "
            f"address", redirected)
    chains = [p["url"] for p in pages.values() if len(p.get("chain") or []) > 1]
    if chains:
        add("fix", "Links", f"{n(len(chains), 'address', 'addresses')} redirect more than once before they answer", chains)
    thin_js = [p["url"] for p in html_pages if p["words"] < 80]
    if thin_js:
        add("blocker", "Content", f"{n(len(thin_js), 'page')} with fewer than 80 words in the HTML before scripts run; "
            "crawlers and assistants that do not run scripts see little or nothing", thin_js)
    noidx = [p["url"] for p in html_pages if "noindex" in " ".join(filter(None, [p.get("robots_meta"),
                                                                                p.get("x_robots_tag")])).lower()]
    if noidx:
        listed = [u for u in noidx if pages[u].get("in_sitemap")]
        add("fix" if listed else "suggestion", "Indexing",
            f"{n(len(noidx), 'page')} ask{'s' if len(noidx) == 1 else ''} not to be indexed" + (f"; {len(listed)} of them are in the sitemap, which sends "
                                                             "mixed signals" if listed else "; check this is intended"), noidx)
    canon_else = [p["url"] for p in html_pages if p.get("canonical_abs") and p["canonical_abs"] not in
                  (p["url"], p.get("final_url"))]
    if canon_else:
        add("suggestion", "Indexing", f"{n(len(canon_else), 'page')} name{'s' if len(canon_else) == 1 else ''} another address as canonical; check each is a "
            "true duplicate", canon_else)
    bad_canon = [p["url"] for p in html_pages if p.get("canonical_abs") in pages and
                 (pages[p["canonical_abs"]].get("status") != 200 or pages[p["canonical_abs"]].get("chain"))]
    if bad_canon:
        add("fix", "Indexing", f"{n(len(bad_canon), 'page')} name{'s' if len(bad_canon) == 1 else ''} a canonical address that redirects or answers an error",
            bad_canon)

    no_title = [p["url"] for p in html_pages if not p["title"]]
    if no_title:
        add("fix", "Titles and descriptions", f"{n(len(no_title), 'page')} without a <title>", no_title)
    by_title = collections.defaultdict(list)
    for p in idx:
        if p["title"]:
            by_title[p["title"].strip().lower()].append(p["url"])
    dup = true_duplicates({k: v for k, v in by_title.items() if len(v) > 1}, pages)
    if dup:
        add("fix", "Titles and descriptions", f"{n(len(dup), 'indexable page')} share{'s' if len(dup) == 1 else ''} its title with another page that is "
            "not one of their language editions", dup)
    long_t = [p["url"] for p in idx if p["title"] and len(p["title"]) > 65]
    if long_t:
        add("suggestion", "Titles and descriptions", f"{n(len(long_t), 'title')} over 65 characters; Google sets no "
            "limit but cuts title links to fit the device width (Google Search Central, title links, updated "
            "10 December 2025)", long_t)
    no_desc = [p["url"] for p in idx if not p.get("description")]
    if no_desc:
        add("fix", "Titles and descriptions", f"{n(len(no_desc), 'indexable page')} without a meta description", no_desc)
    by_desc = collections.defaultdict(list)
    for p in idx:
        if p.get("description"):
            by_desc[p["description"].strip().lower()].append(p["url"])
    dup_d = true_duplicates({k: v for k, v in by_desc.items() if len(v) > 1}, pages)
    if dup_d:
        add("suggestion", "Titles and descriptions", f"{n(len(dup_d), 'page')} with a meta description another page also uses",
            dup_d)
    h1 = [p["url"] for p in idx if len(p["h1"]) != 1]
    if h1:
        add("fix", "Headings", f"{n(len(h1), 'indexable page')} without exactly one <h1>", h1)

    no_lang = [p["url"] for p in html_pages if not p["lang"]]
    if no_lang:
        add("suggestion", "Language", f"{n(len(no_lang), 'page')} without a lang attribute on <html>", no_lang)
    bad_hl = []
    for p in html_pages:
        codes = [c for c, _ in p.get("hreflang", [])]
        if codes and p["url"] not in [h for _, h in p["hreflang"]] and p.get("final_url") not in [h for _, h in p["hreflang"]]:
            bad_hl.append(p["url"])
    if bad_hl:
        add("fix", "Language", f"{n(len(bad_hl), 'page')} listing hreflang alternates but not {'itself' if len(bad_hl) == 1 else 'themselves'}; run the "
            "international-seo skill for the full check", bad_hl)
    no_vp = [p["url"] for p in html_pages if not p.get("viewport")]
    if no_vp:
        add("fix", "Mobile", f"{n(len(no_vp), 'page')} without a viewport meta tag", no_vp)
    mixed = [p["url"] for p in html_pages if p.get("mixed_content")]
    if mixed:
        add("fix", "Security", f"{n(len(mixed), 'HTTPS page')} loading images, scripts or styles over plain HTTP", mixed)
    alt = [p["url"] for p in html_pages if p.get("images_no_alt")]
    if alt:
        add("suggestion", "Images", f"{n(sum(p.get('images_no_alt', 0) for p in html_pages), 'image')} on {n(len(alt), 'page')} "
            "without an alt attribute (use alt=\"\" for decorative images)", alt)
    no_ld = [p["url"] for p in idx if not p["jsonld_types"]]
    if no_ld:
        add("suggestion", "Structured data", f"{n(len(no_ld), 'indexable page')} without structured data; see the "
            "structured-data skill", no_ld)
    ld_err = [p["url"] for p in html_pages if p["jsonld_errors"]]
    if ld_err:
        add("fix", "Structured data", f"{n(len(ld_err), 'page')} with a JSON-LD block that is not valid JSON", ld_err)

    deep = [p["url"] for p in idx if (p.get("depth") or 0) > 3]
    if deep:
        add("suggestion", "Site structure", f"{n(len(deep), 'indexable page')} more than 3 clicks from the start page",
            deep)
    orphans = [u for u in a["sitemap_urls"] if u in pages and not a["inlinks"].get(u) and u != next(iter(pages), "")]
    if orphans:
        add("fix", "Site structure", f"{n(len(orphans), 'page')} in the sitemap that no crawled page links to "
            "(orphans); see the internal-linking skill", orphans)
    sm_bad = [u for u in a["sitemap_urls"] if u in pages and (pages[u].get("status") != 200 or pages[u].get("chain")
                                                            or not indexable(pages[u]))]
    if sm_bad:
        add("fix", "Sitemap", f"{n(len(sm_bad), 'sitemap address', 'sitemap addresses')} that redirect, answer an error, ask not to be indexed or "
            "name another canonical; a sitemap should list only final, indexable addresses", sm_bad)
    not_in = [p["url"] for p in idx if not p.get("in_sitemap")] if a["sitemap"]["count"] else []
    if not_in:
        add("suggestion", "Sitemap", f"{n(len(not_in), 'indexable page')} missing from the sitemap", not_in)
    if not a["sitemap"]["count"]:
        add("fix", "Sitemap", "no sitemap was found" + ("" if a["sitemap"]["declared"] else
                                                       " (robots.txt declares none, and /sitemap.xml gave nothing)"),
            [a["site"] + "/sitemap.xml"])
    nofollow = []
    gen = collections.defaultdict(list)
    for p in html_pages:
        for h, anchor, rel in p.get("internal_links", []):
            if anchor.strip().lower() in GENERIC_ANCHORS:
                gen[p["url"]].append(anchor)
            if "nofollow" in rel:
                nofollow.append(p["url"])
    if gen:
        add("suggestion", "Links", f"{n(sum(len(v) for v in gen.values()), 'internal link')} saying only \"click here\", "
            "\"read more\" or the like; anchor text should say what the page is", list(gen))
    if nofollow:
        add("suggestion", "Links", f"{n(len(nofollow), 'internal link')} with rel=nofollow", nofollow)
    ai_shut = [r for r in a["crawlers"] if r["kind"] == "user" and r["paths"] and not all(r["paths"].values())]
    if ai_shut:
        add("fix", "AI search", "robots.txt closes the home page to assistants' user fetchers: " +
            ", ".join(r["token"] for r in ai_shut) + "; see the ai-crawler-access skill", [a["site"] + "/robots.txt"])
    if not a["llms_txt"]:
        add("suggestion", "AI search", "no llms.txt; Google Search does not use it, other agents may (see the "
            "llms-txt skill)", [a["site"] + "/llms.txt"])
    if a["not_crawled"]:
        add("suggestion", "Crawling", f"{n(len(a['not_crawled']), 'linked page')} not checked because the page limit "
            "was reached; raise --max-pages to include them", a["not_crawled"])
    return out


def report(a, notes):
    pages = a["pages"]
    html_pages = [p for p in pages.values() if "title" in p]
    count = collections.Counter(lvl for lvl, *_ in notes)
    status = collections.Counter(p.get("status") for p in pages.values() if p.get("status") is not None)
    L = [f"# SEO and AI search audit: {urllib.parse.urlsplit(a['site']).netloc} ({a['checked']})", "",
         f"Pages checked: {len(pages)} ({len(html_pages)} HTML pages read). Blockers: {count['blocker']}. "
         f"Fixes: {count['fix']}. Suggestions: {count['suggestion']}.", "",
         "Answer codes: " + ", ".join(f"{k or 'no answer'} x{v}" for k, v in sorted(status.items(), key=lambda x: -x[1])),
         f"robots.txt: {a['robots']['detail']}. Sitemap: {a['sitemap']['count']} addresses in "
         f"{n(len(a['sitemap']['files']), 'file')}. llms.txt: {'present' if a['llms_txt'] else 'not found'}.", ""]
    for lvl, title in (("blocker", "Blockers"), ("fix", "Fixes"), ("suggestion", "Suggestions")):
        items = [n for n in notes if n[0] == lvl]
        if not items:
            continue
        L += [f"## {title}", ""]
        for _, cat, msg, urls in items:
            shown = ", ".join(urls[:10]) + (f", and {len(urls) - 10} more" if len(urls) > 10 else "")
            L += [f"- {cat}: {msg}.", f"  {shown}" if shown else ""]
        L.append("")
    shut = [r["token"] for r in a["crawlers"] if r["paths"] and not all(r["paths"].values())]
    L += ["## AI crawlers on the home page", "",
          f"Closed: {', '.join(shut) or 'none'}. Facts about each crawler from its company's documentation, read "
          f"{a['crawler_facts_read']}.", "",
          "## What this audit did not check", "",
          "- Page speed and Core Web Vitals: the page-speed skill.",
          "- Text that appears only after scripts run, beyond the word count above.",
          "- Links from other sites: the backlink-audit skill. What AI assistants say about the brand.",
          "- Search Console data: the search-console skill reads it live, keyword-research its exports.",
          "- Firewall and CDN rules, which can turn crawlers away whatever robots.txt says.", ""]
    return "\n".join(x for x in L if x is not None)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("url")
    ap.add_argument("--max-pages", type=int, default=100)
    ap.add_argument("--delay", type=float, default=0.5)
    ap.add_argument("--no-sitemap", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out", help="folder for report.md and audit.json")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)
    url = norm(a.url if "://" in a.url else "https://" + a.url)
    log = None if (a.quiet or a.json) else (lambda s: print(s, file=sys.stderr))
    audit = crawl(url, max(1, min(a.max_pages, 2000)), max(0.0, a.delay), not a.no_sitemap, log)
    notes = findings(audit)
    audit["findings"] = [{"level": l, "category": c, "message": m, "urls": u} for l, c, m, u in notes]
    text = report(audit, notes)
    if a.out:
        out = pathlib.Path(a.out)
        out.mkdir(parents=True, exist_ok=True)
        (out / "report.md").write_text(text + "\n", encoding="utf-8")
        (out / "audit.json").write_text(json.dumps(audit, indent=1, default=str), encoding="utf-8")
    print(json.dumps(audit, indent=1, default=str) if a.json else text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
