#!/usr/bin/env python3
"""A backlink audit from free link exports: referring domains, linked pages, anchor text and link types; which links
still exist; links that point at broken pages on the site (to reclaim); and the domains that link to competitors but
not to the site.

Usage:
    python3 backlinks.py links.csv --site example.com
    python3 backlinks.py gsc-latest-links.csv bing-backlinks.csv --site example.com --brand "acme,acme analytics"
    python3 backlinks.py links.csv --site example.com --verify --max-verify 150    fetch each linking page
    python3 backlinks.py links.csv --site example.com --check-targets              status of each linked page
    python3 backlinks.py links.csv --site example.com --competitor rival-a.csv --competitor rival-b.csv
    python3 backlinks.py links.csv --site example.com --ranks top-1m.csv           Tranco rank of each domain
    Add --json for machine output, --out report.md to keep the report.

Reads the CSV exports of Google Search Console (Links: latest links, sample links, top linking sites), Bing Webmaster
Tools (Backlinks, for the site and for the similar sites it compares) and Ahrefs' free webmaster account, or any CSV
with a column for the linking page (or linking site) and, where known, the target page, anchor text and link type.
Comma, semicolon or tab separated, UTF-8 or UTF-16.

--ranks takes the Tranco list of the top million sites (free, tranco-list.eu: rank,domain without a header), to show
how well known each linking site is. It is a popularity list, not a measure of a link's worth.

--verify and --check-targets fetch pages politely: robots.txt is obeyed, one request at a time with a pause, and only
the pages in the files. Observed facts only: no score, no "toxic" label. Standard library only.
"""
import argparse
import codecs
import collections
import csv
import html
import io
import json
import pathlib
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser

UA = "VisibianSkill/1.0 (+https://visibian.com)"
TOKEN = "VisibianSkill"
TWO_PART = {"co.uk", "org.uk", "ac.uk", "gov.uk", "ltd.uk", "plc.uk", "me.uk", "com.au", "net.au", "org.au", "edu.au",
            "gov.au", "co.nz", "org.nz", "co.jp", "ne.jp", "or.jp", "ac.jp", "go.jp", "co.kr", "or.kr", "com.br",
            "com.mx", "com.ar", "com.co", "com.tr", "com.cn", "com.hk", "com.tw", "com.sg", "com.my", "co.in", "co.id",
            "co.za", "co.il", "com.ua", "com.pl", "com.es", "com.pt", "co.th", "com.vn", "com.ph", "com.pk", "com.eg",
            "com.sa", "com.ng", "co.ke", "github.io", "blogspot.com", "wordpress.com", "substack.com", "medium.com",
            "netlify.app", "vercel.app", "pages.dev", "web.app"}
GENERIC = {"", "here", "click here", "read more", "learn more", "more", "this", "link", "website", "site", "source",
           "this article", "this post", "this page", "this link", "homepage", "home page", "visit", "visit site",
           "visit website", "see more", "details", "more info", "go", "url", "check it out", "this site", "read",
           "continue reading", "find out more", "via", "[1]", "1", "image", "(image)", "logo"}


# ------------------------------------------------------------------ reading the exports

def decode(raw):
    if raw.startswith(codecs.BOM_UTF16_LE) or raw.startswith(codecs.BOM_UTF16_BE):
        return raw.decode("utf-16")
    if raw.startswith(codecs.BOM_UTF8):
        return raw[3:].decode("utf-8", "replace")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("latin-1")


def role(h):
    h = re.sub(r"\s+", " ", h.strip().lower().replace("_", " "))
    if "anchor" in h:
        return "anchor"
    if h in ("nofollow", "no follow", "is nofollow"):
        return "nofollow"
    if h in ("ugc", "sponsored"):
        return h
    if h in ("type", "link type", "rel", "link rel", "follow", "dofollow", "link attributes", "attributes"):
        return "rel"
    if "first seen" in h or "first found" in h or h in ("found", "discovered"):
        return "first_seen"
    if "last seen" in h or "last crawled" in h or "last checked" in h:
        return "last_seen"
    if re.search(r"(pages|links|backlinks|count|number)$", h):
        return "count"
    if "target" in h or h in ("linked page", "to url", "url to", "destination", "destination url", "link url"):
        return "target"
    if re.search(r"(linking|referring|source|from)\b.*\b(page|url)$", h) or h in (
            "source", "from", "url from", "backlink", "backlink url", "referring url", "linking url", "url"):
        return "source"
    if re.search(r"^(linking |referring |source )?(site|domain|host|website)$", h):
        return "domain"
    return None


def read_file(path):
    text = decode(pathlib.Path(path).read_bytes())
    first = text.splitlines()[0] if text.strip() else ""
    delim = "\t" if first.count("\t") > max(first.count(","), first.count(";")) else \
        ";" if first.count(";") > first.count(",") else ","
    rows = list(csv.reader(io.StringIO(text), delimiter=delim))
    if not rows:
        return [], {}
    head = rows[0]
    roles = {}
    for i, h in enumerate(head):
        r = role(h)
        if r and r not in roles:
            roles[r] = i
    if "source" in roles:
        roles.pop("domain", None)
    if "source" not in roles and "domain" not in roles:
        # an unknown export: the first column that holds addresses is the linking page
        for i, v in enumerate(rows[1] if len(rows) > 1 else []):
            if v.startswith("http"):
                roles["source"] = i
                break
    out = []
    for r in rows[1:]:
        if not r or not any(c.strip() for c in r):
            continue
        g = lambda k: r[roles[k]].strip() if k in roles and roles[k] < len(r) else ""
        rec = {"source": g("source"), "domain": g("domain"), "target": g("target"), "anchor": g("anchor"),
               "rel": rel_of(g("rel"), g("nofollow"), g("ugc"), g("sponsored")),
               "first_seen": g("first_seen"), "last_seen": g("last_seen"), "count": num(g("count")), "file": str(path),
               "has_anchor": "anchor" in roles}
        if rec["source"] and not rec["source"].startswith("http"):
            rec["source"] = "https://" + rec["source"].lstrip("/")
        if not rec["domain"] and rec["source"]:
            rec["domain"] = host(rec["source"])
        rec["domain"] = registrable(rec["domain"].lower().strip()) if rec["domain"] else ""
        if rec["domain"]:
            out.append(rec)
    return out, {k: head[i] for k, i in roles.items()}


def num(v):
    try:
        return int(float(v.replace(",", "")))
    except (ValueError, AttributeError):
        return None


def truthy(v):
    return v.strip().lower() in ("true", "1", "yes", "y", "x")


def rel_of(rel, nofollow, ugc, sponsored):
    found = set()
    for word in ("nofollow", "ugc", "sponsored"):
        if word in rel.lower():
            found.add(word)
    if nofollow and truthy(nofollow):
        found.add("nofollow")
    if ugc and truthy(ugc):
        found.add("ugc")
    if sponsored and truthy(sponsored):
        found.add("sponsored")
    if found:
        return " ".join(sorted(found))
    if "follow" in rel.lower() or nofollow or ugc or sponsored:
        return "followed"
    return ""


def host(url):
    try:
        h = urllib.parse.urlsplit(url if "://" in url else "https://" + url).hostname or ""
    except ValueError:
        return ""
    return h[4:] if h.startswith("www.") else h


def registrable(h):
    """The site a host belongs to: blog.example.co.uk is example.co.uk. Approximate: no public suffix list."""
    h = host(h) if "/" in h or ":" in h else (h[4:] if h.startswith("www.") else h)
    parts = h.split(".")
    if len(parts) <= 2:
        return h
    tail2 = ".".join(parts[-2:])
    return ".".join(parts[-3:]) if tail2 in TWO_PART else tail2


# ------------------------------------------------------------------ the profile

def anchor_kind(a, site, brand):
    t = html.unescape(a or "").strip().lower()
    if not t:
        return "empty or image"
    if re.match(r"^(https?://|www\.)|^[a-z0-9-]+(\.[a-z0-9-]+)+(/\S*)?$", t):
        return "address"
    if any(b and b in t for b in brand) or site.split(".")[0] in t.replace(" ", ""):
        return "brand"
    if t in GENERIC:
        return "generic"
    return "words"


def profile(rows, site, brand, ranks=None):
    site_reg = registrable(host(site))
    rows = [r for r in rows if r["domain"] != site_reg]
    page_rows = [r for r in rows if r["source"]]
    domains = collections.Counter()
    for r in rows:
        domains[r["domain"]] += (r["count"] or 1) if not r["source"] else 1
    pages = {r["source"] for r in page_rows}
    targets = collections.Counter(r["target"] for r in page_rows if r["target"])
    anchors = collections.Counter(anchor_kind(r["anchor"], site_reg, brand) for r in page_rows if r["has_anchor"])
    top_anchor = collections.Counter(r["anchor"].strip() for r in page_rows if r["anchor"].strip())
    rels = collections.Counter(r["rel"] for r in page_rows if r["rel"])
    by_domain_pages = collections.Counter(r["domain"] for r in page_rows)
    sitewide = [d for d, c in by_domain_pages.items() if c >= 50]
    out = {"site": site_reg, "rows": len(rows), "referring_domains": len(domains), "referring_pages": len(pages),
           "top_domains": [{"domain": d, "links": c, "rank": (ranks or {}).get(d)} for d, c in domains.most_common(25)],
           "top_targets": [{"page": t, "links": c} for t, c in targets.most_common(20)],
           "anchors": dict(anchors), "top_anchors": top_anchor.most_common(15), "rel": dict(rels),
           "sitewide": sitewide}
    if ranks:
        tiers = collections.Counter()
        for d in domains:
            rk = ranks.get(d)
            tiers["top 10,000" if rk and rk <= 10000 else "top 100,000" if rk and rk <= 100000 else
                  "top 1,000,000" if rk else "not in the list"] += 1
        out["rank_tiers"] = dict(tiers)
    return out


def load_ranks(path):
    ranks = {}
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) >= 2 and parts[0].isdigit():
                ranks.setdefault(registrable(parts[1].lower()), int(parts[0]))
    return ranks


def gap(rows, competitor_sets, site):
    """Domains that link to competitors and not to the site, with how many competitors each links to."""
    site_reg = registrable(host(site))
    ours = {r["domain"] for r in rows}
    seen = collections.defaultdict(set)
    for name, crow in competitor_sets.items():
        for r in crow:
            if r["domain"] not in ours and r["domain"] != site_reg:
                seen[r["domain"]].add(name)
    return sorted(([d, sorted(c)] for d, c in seen.items()), key=lambda x: (-len(x[1]), x[0]))


# ------------------------------------------------------------------ fetching

class Polite:
    def __init__(self, delay=1.0, timeout=20):
        self.delay, self.timeout, self.robots, self.last = delay, timeout, {}, 0.0

    def allowed(self, url):
        p = urllib.parse.urlsplit(url)
        root = f"{p.scheme}://{p.netloc}"
        if root not in self.robots:
            rp = urllib.robotparser.RobotFileParser()
            try:
                status, body, _ = self.get(root + "/robots.txt", check=False, limit=500_000)
                rp.parse(body.splitlines() if status == 200 else [])
            except Exception:
                rp.parse([])
            self.robots[root] = rp
        return self.robots[root].can_fetch(TOKEN, url)

    def get(self, url, check=True, limit=3_000_000):
        if check and not self.allowed(url):
            return "robots", "", url
        wait = self.delay - (time.time() - self.last)
        if wait > 0:
            time.sleep(wait)
        self.last = time.time()
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*;q=0.5"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                ctype = r.headers.get("Content-Type", "")
                charset = r.headers.get_content_charset() or "utf-8"
                body = r.read(limit).decode(charset, "replace") if ("html" in ctype or "text" in ctype or not ctype) \
                    else ""
                return r.status, body, r.geturl()
        except urllib.error.HTTPError as e:
            e.close()
            return e.code, "", url
        except Exception as e:
            return f"no answer ({type(e).__name__})", "", url


A_TAG = re.compile(r"<a\b([^>]*)>(.*?)</a>", re.I | re.S)


def attr(tag, name):
    m = re.search(r"\b" + name + r"""\s*=\s*("([^"]*)"|'([^']*)'|([^\s>]+))""", tag, re.I)
    return html.unescape(next(g for g in m.groups()[1:] if g is not None)) if m else None


def links_to(body, base, site_reg):
    found = []
    for m in A_TAG.finditer(body):
        href = attr(m.group(1), "href")
        if not href:
            continue
        absu = urllib.parse.urljoin(base, href.strip())
        if registrable(host(absu)) == site_reg:
            text = re.sub(r"<[^>]+>", " ", m.group(2))
            alt = attr(m.group(2), "alt") if "<img" in m.group(2).lower() else None
            anchor = html.unescape(re.sub(r"\s+", " ", text)).strip() or (f"(image: {alt})" if alt else "(image)")
            rel = (attr(m.group(1), "rel") or "").lower()
            kinds = sorted({w for w in ("nofollow", "ugc", "sponsored") if w in rel.split()})
            found.append({"target": absu, "anchor": anchor, "rel": " ".join(kinds) or "followed"})
    return found


def verify(rows, site, max_pages, delay, log=None):
    site_reg = registrable(host(site))
    pages = list(dict.fromkeys(r["source"] for r in rows if r["source"]))[:max_pages]
    fetcher, out = Polite(delay), []
    for i, u in enumerate(pages, 1):
        status, body, final = fetcher.get(u)
        rec = {"page": u, "status": status, "links": []}
        if status == 200:
            rec["links"] = links_to(body, final, site_reg)
            rec["state"] = "live" if rec["links"] else "no link found"
        elif status == "robots":
            rec["state"] = "not checked (robots.txt)"
        else:
            rec["state"] = "page unreachable"
        out.append(rec)
        if log:
            log(f"{i:>4}/{len(pages)} {rec['state']:<26} {u}")
    return out


def check_targets(rows, site, delay, max_pages=300, log=None):
    targets = list(dict.fromkeys(r["target"] for r in rows if r["target"]))[:max_pages]
    fetcher, out = Polite(delay), []
    linked = collections.Counter(r["target"] for r in rows if r["target"])
    doms = collections.defaultdict(set)
    for r in rows:
        if r["target"]:
            doms[r["target"]].add(r["domain"])
    for t in targets:
        status, _, final = fetcher.get(t, check=False, limit=200_000)
        out.append({"page": t, "status": status, "final": final if final != t else None, "links": linked[t],
                    "domains": len(doms[t])})
        if log:
            log(f"{status} {t}")
    return out


# ------------------------------------------------------------------ the report

def pct(part, whole):
    return f"{part / whole * 100:.0f}%" if whole else ""


def render(r):
    p = r["profile"]
    L = [f"# Backlink audit: {p['site']} ({r['date']})", "",
         f"Read: {', '.join(r['files'])}. {p['rows']:,} rows; {p['referring_domains']:,} linking sites; "
         f"{p['referring_pages']:,} linking pages.", ""]
    if r.get("columns"):
        L += ["Columns used: " + "; ".join(f"{pathlib.Path(f).name}: " + ", ".join(f"{k} from \"{v}\""
                                                                               for k, v in c.items())
                                           for f, c in r["columns"].items()), ""]
    L += ["## Linking sites", "", "| Site | Links | Tranco rank |" if r.get("ranked") else "| Site | Links |",
          "|---|---|---|" if r.get("ranked") else "|---|---|"]
    for d in p["top_domains"]:
        L.append(f"| {d['domain']} | {d['links']:,} |" + (f" {d['rank'] or ''} |" if r.get("ranked") else ""))
    if p.get("rank_tiers"):
        L += ["", "Linking sites by the Tranco list: " + "; ".join(f"{k}: {v}" for k, v in p["rank_tiers"].items())
              + ". The list measures how visited and linked a site is, not what a link from it is worth."]
    if p["sitewide"]:
        L += ["", f"Sites that link from 50 or more pages (a footer, sidebar or blogroll): {', '.join(p['sitewide'])}."]
    if p["top_targets"]:
        L += ["", "## The site's pages with the most links", "", "| Page | Links |", "|---|---|"]
        L += [f"| {t['page']} | {t['links']:,} |" for t in p["top_targets"]]
    total_a = sum(p["anchors"].values())
    if total_a:
        L += ["", "## Anchor text", "", "| Kind | Links | Share |", "|---|---|---|"]
        L += [f"| {k} | {v:,} | {pct(v, total_a)} |" for k, v in sorted(p["anchors"].items(), key=lambda x: -x[1])]
        L += ["", "Most used: " + "; ".join(f"\"{a}\" ({c})" for a, c in p["top_anchors"][:10])]
    total_r = sum(p["rel"].values())
    if total_r:
        L += ["", "Link types in the exports: " + "; ".join(f"{k} {pct(v, total_r)}" for k, v in
                                                           sorted(p["rel"].items(), key=lambda x: -x[1])) + "."]
    if r.get("verified"):
        v = r["verified"]
        c = collections.Counter(x["state"] for x in v)
        live_links = [l for x in v for l in x["links"]]
        rels = collections.Counter(l["rel"] for l in live_links)
        L += ["", f"## Checked live ({len(v)} linking pages)", "",
              "; ".join(f"{k}: {n}" for k, n in c.most_common()) + ".",
              "Link types on the live pages: " + ("; ".join(f"{k} {pct(n, len(live_links))}" for k, n in
                                                            rels.most_common()) or "none found") + "."]
        gone = [x["page"] for x in v if x["state"] == "no link found"]
        if gone:
            L += ["", "Pages that load without a link to the site: the link was removed, or the page links through "
                  "its own redirect or a script. Look at each before asking the site about it:", ""]
            L += [f"- {g}" for g in gone[:40]] + ([f"- and {len(gone) - 40} more"] if len(gone) > 40 else [])
    if r.get("targets"):
        broken = [t for t in r["targets"] if not (isinstance(t["status"], int) and t["status"] < 400)]
        L += ["", f"## Linked pages on the site ({len(r['targets'])} checked)", ""]
        if broken:
            L += [f"{len(broken)} linked pages do not answer 200 or a redirect. Restore each page, or redirect it "
                  f"(301) to the closest live page, so the links count again:", "",
                  "| Page | Answer | Links | Linking sites |", "|---|---|---|---|"]
            L += [f"| {t['page']} | {t['status']} | {t['links']} | {t['domains']} |"
                  for t in sorted(broken, key=lambda t: -t["domains"])]
        else:
            L.append("Every linked page answers.")
        moved = [t for t in r["targets"] if t["final"]]
        if moved:
            L += ["", f"{len(moved)} linked pages redirect; update the links you control to the final address."]
    if r.get("gap") is not None:
        g = r["gap"]
        L += ["", f"## Sites that link to competitors and not to {p['site']}", "",
              f"{len(g):,} sites. The ones that link to more than one competitor come first: they already cover the "
              f"topic and link out.", "", "| Site | Links to |", "|---|---|"]
        L += [f"| {d} | {', '.join(c)} |" for d, c in g[:60]]
        if len(g) > 60:
            L.append(f"| and {len(g) - 60} more | |")
    L += ["", "## What this cannot tell", "",
          "- Links the exports do not hold: each tool sees only part of the web, so read the numbers as a sample.",
          "- What a link is worth to rankings: no tool outside Google knows, and this report does not guess.",
          "- Whether AI assistants read or cite the linking pages."]
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("files", nargs="+")
    ap.add_argument("--site", required=True, help="the site the links point to, such as example.com")
    ap.add_argument("--brand", default="", help="brand words, comma separated, for the anchor text")
    ap.add_argument("--competitor", action="append", default=[], help="a competitor's link export (repeatable)")
    ap.add_argument("--ranks", help="the Tranco list (rank,domain)")
    ap.add_argument("--verify", action="store_true", help="fetch each linking page and look for the link")
    ap.add_argument("--max-verify", type=int, default=100)
    ap.add_argument("--check-targets", action="store_true", help="check the status of each linked page")
    ap.add_argument("--delay", type=float, default=1.0)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)
    log = None if (a.quiet or a.json) else (lambda s: print(s, file=sys.stderr))
    rows, columns = [], {}
    for f in a.files:
        got, cols = read_file(f)
        rows += got
        columns[f] = cols
    if not rows:
        print("No links found in the files. Check that each has a column for the linking page or site.",
              file=sys.stderr)
        return 1
    brand = [b.strip().lower() for b in a.brand.split(",") if b.strip()]
    ranks = load_ranks(a.ranks) if a.ranks else None
    r = {"date": time.strftime("%Y-%m-%d"), "files": [pathlib.Path(f).name for f in a.files], "columns": columns,
         "ranked": bool(ranks), "profile": profile(rows, a.site, brand, ranks)}
    if a.competitor:
        comp = {}
        for f in a.competitor:
            got, _ = read_file(f)
            comp[pathlib.Path(f).stem] = got
        r["gap"] = gap(rows, comp, a.site)
    if a.verify:
        r["verified"] = verify(rows, a.site, a.max_verify, max(0.0, a.delay), log)
    if a.check_targets:
        r["targets"] = check_targets(rows, a.site, max(0.0, a.delay), log=log)
    text = json.dumps(r, indent=1, default=str) if a.json else render(r)
    if a.out:
        pathlib.Path(a.out).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
