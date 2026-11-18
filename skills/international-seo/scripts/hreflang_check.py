#!/usr/bin/env python3
"""Check hreflang on a multilingual or multi-country site the way Google reads it.

Usage:
    python3 hreflang_check.py https://example.com/ https://example.com/de/        pages to check (and their alternates)
    python3 hreflang_check.py --audit seo-audit/audit.json                        every page of a seo-audit crawl
    Add --json for machine output, --max-fetch 80 to fetch more alternates (default 60).

Per Google ("Tell Google about localized versions of your page", updated 21 September 2026): a language code in ISO
639-1, optionally a script in ISO 15924 (zh-Hant) and a region in ISO 3166-1 Alpha 2 (en-GB); x-default for the
fallback; every page lists itself; and if page X names page Y, Y must name X back, or the pair may be ignored. It also
checks that each alternate answers 200, is indexable and names itself canonical. Standard library only;
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

LANGS = set("""aa ab ae af ak am an ar as av ay az ba be bg bh bi bm bn bo br bs ca ce ch co cr cs cu cv cy da de dv dz ee
el en eo es et eu fa ff fi fj fo fr fy ga gd gl gn gu gv ha he hi ho hr ht hu hy hz ia id ie ig ii ik io is it iu ja jv ka
kg ki kj kk kl km kn ko kr ks ku kv kw ky la lb lg li ln lo lt lu lv mg mh mi mk ml mn mr ms mt my na nb nd ne ng nl nn no
nr nv ny oc oj om or os pa pi pl ps pt qu rm rn ro ru rw sa sc sd se sg si sk sl sm sn so sq sr ss st su sv sw ta te tg th
ti tk tl tn to tr ts tt tw ty ug uk ur uz ve vi vo wa wo xh yi yo za zh zu""".split())
REGIONS = set("""AD AE AF AG AI AL AM AO AQ AR AS AT AU AW AX AZ BA BB BD BE BF BG BH BI BJ BL BM BN BO BQ BR BS BT BV BW BY
BZ CA CC CD CF CG CH CI CK CL CM CN CO CR CU CV CW CX CY CZ DE DJ DK DM DO DZ EC EE EG EH ER ES ET FI FJ FK FM FO FR GA GB
GD GE GF GG GH GI GL GM GN GP GQ GR GS GT GU GW GY HK HM HN HR HT HU ID IE IL IM IN IO IQ IR IS IT JE JM JO JP KE KG KH KI
KM KN KP KR KW KY KZ LA LB LC LI LK LR LS LT LU LV LY MA MC MD ME MF MG MH MK ML MM MN MO MP MQ MR MS MT MU MV MW MX MY MZ
NA NC NE NF NG NI NL NO NP NR NU NZ OM PA PE PF PG PH PK PL PM PN PR PS PT PW PY QA RE RO RS RU RW SA SB SC SD SE SG SH SI
SJ SK SL SM SN SO SR SS ST SV SX SY SZ TC TD TF TG TH TJ TK TL TM TN TO TR TT TV TW TZ UA UG UM US UY UZ VA VC VE VG VI VN
VU WF WS YE YT ZA ZM ZW""".split())
COMMON_MISTAKES = {"uk": "GB is the region code for the United Kingdom (en-GB)", "jp": "the language code for Japanese is ja",
                   "cn": "the language code for Chinese is zh (zh-CN for China)", "kr": "the language code for Korean is ko",
                   "dk": "the language code for Danish is da", "se": "the language code for Swedish is sv",
                   "gr": "the language code for Greek is el", "cz": "the language code for Czech is cs",
                   "eu-": "EU is not a country code"}


def check_code(code):
    """None if valid, else why not."""
    c = code.strip()
    if c.lower() == "x-default":
        return None
    if "_" in c:
        return f"\"{c}\" uses an underscore; hreflang uses a hyphen ({c.replace('_', '-')})"
    parts = c.split("-")
    lang = parts[0].lower()
    if lang not in LANGS:
        hint = COMMON_MISTAKES.get(lang)
        return f"\"{c}\": {lang} is not an ISO 639-1 language code" + (f" ({hint})" if hint else "")
    rest = parts[1:]
    if rest and len(rest[0]) == 4 and rest[0].isalpha():
        rest = rest[1:]                     # an ISO 15924 script such as Hant or Hans
    if len(rest) > 1:
        return f"\"{c}\" has more parts than language, script and region"
    if rest:
        reg = rest[0].upper()
        if reg == "UK":
            return f"\"{c}\": {COMMON_MISTAKES['uk']}"
        if reg.isdigit():
            return (f"\"{c}\": {rest[0]} is a UN area code, which Google does not support (it names es-419 as an "
                    f"example); use the language alone ({lang}) or one code per country, such as {lang}-MX")
        if reg not in REGIONS:
            return f"\"{c}\": {rest[0]} is not an ISO 3166-1 Alpha 2 region code"
    return None


def norm(u, base=""):
    p = urllib.parse.urlsplit(urllib.parse.urljoin(base, (u or "").strip()))
    return urllib.parse.urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path or "/", p.query, "")) if p.scheme else None


def hreflangs(doc, headers, base):
    head = re.search(r"<head\b.*?</head>", doc, re.S | re.I)
    head = head.group(0) if head else doc[:30000]
    out = [(page_check.attr(t, "hreflang"), norm(page_check.attr(t, "href"), base))
           for t in re.findall(r"<link\b[^>]*>", head, re.I)
           if (page_check.attr(t, "rel") or "").lower() == "alternate" and page_check.attr(t, "hreflang")]
    for part in re.split(r",(?=\s*<)", (headers or {}).get("Link", "") or (headers or {}).get("link", "")):
        m = re.match(r'\s*<([^>]+)>(.*)', part)
        if m and re.search(r'rel="?alternate', m.group(2), re.I):
            hl = re.search(r'hreflang="?([^";]+)', m.group(2), re.I)
            if hl:
                out.append((hl.group(1), norm(m.group(1), base)))
    return out


class Site:
    def __init__(self, max_fetch=60):
        self.cache, self.max_fetch = {}, max_fetch

    def page(self, url):
        if url in self.cache:
            return self.cache[url]
        if len(self.cache) >= self.max_fetch:
            return None
        g = page_check.get(url)
        rec = {"status": g["status"], "final": norm(g["url"]), "alts": [], "lang": None, "canonical": None,
               "noindex": False}
        if g["status"] == 200 and g["body"]:
            f = page_check.page_facts(g["body"], g["headers"])
            rec.update(alts=hreflangs(g["body"], g["headers"], g["url"]), lang=f["lang"],
                       canonical=norm(f["canonical"], g["url"]) if f["canonical"] else None,
                       noindex="noindex" in " ".join(filter(None, [f["robots_meta"], f["x_robots_tag"]])).lower())
        self.cache[url] = rec
        return rec


def check(urls, max_fetch=60):
    site, issues = Site(max_fetch), []
    add = lambda lvl, url, msg: issues.append({"level": lvl, "url": url, "message": msg})
    for url in urls:
        p = site.page(url)
        if not p or p["status"] != 200:
            add("fix", url, f"answered {p['status'] if p else 'not fetched'}")
            continue
        if not p["alts"]:
            continue
        codes = collections.defaultdict(set)
        for code, href in p["alts"]:
            why = check_code(code or "")
            if why:
                add("fix", url, why)
            codes[(code or "").lower()].add(href)
        for code, hrefs in codes.items():
            if len(hrefs) > 1:
                add("fix", url, f"hreflang \"{code}\" points at {len(hrefs)} different addresses: {', '.join(sorted(hrefs))}")
        targets = {h for _, h in p["alts"]}
        if url not in targets and p["final"] not in targets:
            add("fix", url, "does not list itself among its hreflang alternates")
        if "x-default" not in codes:
            add("suggestion", url, "no x-default; consider one for readers who match none of the languages")
        own = [c for c, h in p["alts"] if h in (url, p["final"])]
        if own and p["lang"] and own[0].split("-")[0].lower() != p["lang"].split("-")[0].lower():
            add("suggestion", url, f"lists itself as \"{own[0]}\" while <html lang> says \"{p['lang']}\"")
        if p["canonical"] and p["canonical"] not in (url, p["final"]):
            add("fix", url, f"names {p['canonical']} as canonical while carrying hreflang; a page that names another "
                            "as canonical is marked as a duplicate of it, which undoes its own language entry")
        for code, href in p["alts"]:
            if href in (url, p["final"]) or (code or "").lower() == "x-default":
                continue
            q = site.page(href)
            if q is None:
                add("suggestion", url, f"{href} not checked (fetch limit reached; raise --max-fetch)")
                continue
            if q["status"] != 200 or (q["final"] and q["final"] != href):
                add("fix", url, f"alternate {code} {href} answered {q['status']}" +
                    (f" and moved to {q['final']}" if q["final"] and q["final"] != href else ""))
                continue
            if q["noindex"]:
                add("fix", url, f"alternate {code} {href} asks not to be indexed")
            if q["canonical"] and q["canonical"] != href:
                add("fix", url, f"alternate {code} {href} names {q['canonical']} as canonical")
            back = {h for _, h in q["alts"]}
            if url not in back and p["final"] not in back:
                add("fix", url, f"no return link: {href} ({code}) does not name this page back")
    return issues, len(site.cache)


def render(issues, n_pages, n_fetched):
    L = [f"# hreflang check: {n_pages} pages, {n_fetched} addresses fetched", ""]
    for lvl in ("fix", "suggestion"):
        items = [i for i in issues if i["level"] == lvl]
        L += [f"## {'Fixes' if lvl == 'fix' else 'Suggestions'} ({len(items)})", ""]
        by_msg = collections.defaultdict(list)
        for i in items:
            by_msg[i["message"]].append(i["url"])
        L += [f"- {m}: {', '.join(sorted(set(u))[:5])}" + (f" and {len(set(u)) - 5} more" if len(set(u)) > 5 else "")
              for m, u in by_msg.items()] or ["- none"]
        L.append("")
    L.append("Rules from Google Search Central, \"Tell Google about localized versions of your page\", updated "
             "21 September 2026.")
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("urls", nargs="*")
    ap.add_argument("--audit")
    ap.add_argument("--max-fetch", type=int, default=60)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    urls = [norm(u if "://" in u else "https://" + u) for u in a.urls]
    if a.audit:
        with open(a.audit, encoding="utf-8") as f:
            audit = json.load(f)
        urls += [u for u, p in audit["pages"].items() if p.get("hreflang")]
    if not urls:
        ap.error("give addresses or --audit")
    issues, fetched = check(urls, max(len(urls) + 5, a.max_fetch))
    print(json.dumps({"issues": issues, "fetched": fetched}, indent=1) if a.json else render(issues, len(urls), fetched))
    return 0


if __name__ == "__main__":
    sys.exit(main())
