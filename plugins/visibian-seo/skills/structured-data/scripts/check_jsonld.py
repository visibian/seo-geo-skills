#!/usr/bin/env python3
"""Check the JSON-LD structured data in a page, a file or a URL.

Usage:
    python3 check_jsonld.py page.html                    every <script type="application/ld+json"> block in the file
    python3 check_jsonld.py https://example.com/pricing  the same, fetched (raw HTML, no scripts run)
    python3 check_jsonld.py data.jsonld                  a JSON or JSON-LD file
    Add --json for machine output.

What it checks:
  - each block parses as JSON, names schema.org in @context and gives every node a @type;
  - Google's required properties for the types listed in RULES, and its recommended ones as notes
    (Google Search Central's structured data pages, last updated 8 September 2026);
  - dates in ISO 8601 form and absolute URLs where schema.org expects a URL;
  - in a page, that names, headlines and descriptions in the markup also appear in the page text, since Google asks
    that everything in the markup be visible on the page.
It does not run Google's Rich Results Test, and passing it does not mean a rich result or an AI citation will follow.

Standard library only.
"""
import argparse
import html
import json
import pathlib
import re
import sys
import urllib.request

UA = "VisibianSkill/1.0 (+https://visibian.com)"

# type: (required, one-of groups, recommended). Paths use dots for nested properties.
RULES = {
    "Product": (["name"], [["review", "aggregateRating", "offers"]], ["aggregateRating", "offers", "review"]),
    "Offer": ([], [["price", "priceSpecification.price"]], ["availability", "priceCurrency", "priceValidUntil"]),
    "AggregateOffer": (["lowPrice", "priceCurrency"], [], ["highPrice", "offerCount"]),
    "SoftwareApplication": (["name", "offers.price"], [["aggregateRating", "review"]],
                            ["applicationCategory", "operatingSystem"]),
    "LocalBusiness": (["address", "name"], [], ["geo", "openingHoursSpecification", "telephone", "url", "priceRange"]),
    "Organization": ([], [], ["name", "url", "logo", "description", "sameAs", "address", "contactPoint"]),
    "Article": ([], [], ["headline", "image", "author", "datePublished", "dateModified"]),
    "BreadcrumbList": (["itemListElement"], [], []),
    "ListItem": (["name", "position"], [], ["item"]),
    "Event": (["name", "startDate", "location"], [], ["description", "endDate", "eventStatus"]),
    "Review": (["author", "itemReviewed", "reviewRating.ratingValue"], [], ["datePublished"]),
    "AggregateRating": (["ratingValue"], [["ratingCount", "reviewCount"]], ["bestRating", "worstRating"]),
}
# subtypes that follow their parent's rules
ALIAS = {
    "WebApplication": "SoftwareApplication", "MobileApplication": "SoftwareApplication",
    "NewsArticle": "Article", "BlogPosting": "Article", "TechArticle": "Article",
    "Restaurant": "LocalBusiness", "Store": "LocalBusiness", "Dentist": "LocalBusiness",
    "LegalService": "LocalBusiness", "MedicalBusiness": "LocalBusiness", "ProfessionalService": "LocalBusiness",
    "Corporation": "Organization", "OnlineBusiness": "Organization", "OnlineStore": "Organization",
}
NOTES = {
    "FAQPage": "Google stopped showing FAQ rich results on 7 May 2026 (Search Central documentation updates, "
               "8 May 2026). The markup is still valid schema.org and does no harm, but expect no rich result.",
    "HowTo": "Google retired How-to rich results in 2023 (Search Central blog, August 2023). The markup is valid "
             "schema.org but earns no rich result.",
}
DATE_KEYS = {"datePublished", "dateModified", "dateCreated", "startDate", "endDate", "uploadDate", "foundingDate",
             "priceValidUntil", "validFrom", "validThrough"}
URL_KEYS = {"url", "logo", "image", "item", "sameAs", "thumbnailUrl", "contentUrl", "@id"}
VISIBLE_KEYS = ("name", "headline", "description")
ISO = re.compile(r"^\d{4}-\d{2}-\d{2}([T ]\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}:?\d{2})?)?$")


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read(5 * 1024 * 1024).decode("utf-8", "replace")


def blocks_from_html(text):
    pat = re.compile(r'<script[^>]+type\s*=\s*["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.S | re.I)
    return [m.group(1).strip() for m in pat.finditer(text)]


def visible_text(text):
    t = re.sub(r"<(script|style|noscript|template)[^>]*>.*?</\1>", " ", text, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", html.unescape(t)).lower()


def types_of(node):
    t = node.get("@type")
    return [t] if isinstance(t, str) else [x for x in (t or []) if isinstance(x, str)]


def get(node, path):
    cur = node
    for part in path.split("."):
        if isinstance(cur, list):
            cur = next((c for c in cur if isinstance(c, dict) and part in c), cur[0] if cur else None)
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def walk(value, where, out):
    """Every node (a dict with @type) in a block, with a readable location."""
    if isinstance(value, dict):
        if "@type" in value:
            out.append((where, value))
        for k, v in value.items():
            if k != "@context":
                walk(v, f"{where}.{k}", out)
    elif isinstance(value, list):
        for i, v in enumerate(value):
            walk(v, f"{where}[{i}]", out)


def check_node(where, node, page_text, findings):
    names = types_of(node)
    if not names:
        findings.append(("error", where, "a node without @type"))
        return
    for t in names:
        if t in NOTES:
            findings.append(("note", where, f"{t}: {NOTES[t]}"))
        rule = RULES.get(ALIAS.get(t, t))
        if not rule:
            continue
        required, one_of, recommended = rule
        for p in required:
            if get(node, p) in (None, "", []):
                findings.append(("error", where, f"{t} is missing required property {p}"))
        for group in one_of:
            if all(get(node, p) in (None, "", []) for p in group):
                findings.append(("error", where, f"{t} needs one of: {', '.join(group)}"))
        for p in recommended:
            if get(node, p) in (None, "", []):
                findings.append(("note", where, f"{t} could add recommended property {p}"))
    for k, v in node.items():
        vals = v if isinstance(v, list) else [v]
        for x in vals:
            if not isinstance(x, str):
                continue
            if k in DATE_KEYS and not ISO.match(x.strip()):
                findings.append(("warning", where, f"{k} is not an ISO 8601 date: {x!r}"))
            if k in URL_KEYS and not re.match(r"^https?://", x.strip()) and not x.startswith("#"):
                findings.append(("warning", where, f"{k} is not an absolute URL: {x!r}"))
    if page_text:
        for k in VISIBLE_KEYS:
            v = node.get(k)
            if isinstance(v, str) and len(v) >= 3:
                needle = re.sub(r"\s+", " ", html.unescape(v)).strip().lower()
                if needle and needle[:80] not in page_text:
                    findings.append(("warning", where, f"{k} does not appear in the page text: {v[:80]!r}"))


def check(blocks, page_text=""):
    findings, nodes = [], []
    for i, raw in enumerate(blocks):
        where = f"block {i + 1}"
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            findings.append(("error", where, f"not valid JSON: {e.msg} at line {e.lineno}, column {e.colno}"))
            continue
        top = data if isinstance(data, list) else [data]
        for d in top:
            ctx = json.dumps(d.get("@context", "")) if isinstance(d, dict) else ""
            if isinstance(d, dict) and "schema.org" not in ctx:
                findings.append(("error", where, "@context does not name schema.org"))
        found = []
        walk(data, where, found)
        if not found:
            findings.append(("error", where, "no node with @type"))
        for w, node in found:
            nodes.append((w, types_of(node)))
            check_node(w, node, page_text, findings)
    return nodes, findings


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("source", help="an HTML file, a JSON or JSON-LD file, or a URL")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    src = a.source
    if re.match(r"^https?://", src):
        text, is_html = fetch(src), True
    else:
        text = pathlib.Path(src).read_text(encoding="utf-8", errors="replace")
        is_html = not src.lower().endswith((".json", ".jsonld")) and "<" in text[:2000]
    blocks = blocks_from_html(text) if is_html else [text]
    page_text = visible_text(text) if is_html else ""
    if is_html and not blocks:
        print("No JSON-LD blocks found in the raw HTML. If the site adds them with JavaScript, crawlers that do not "
              "run scripts will not see them.")
        return 0
    nodes, findings = check(blocks, page_text)
    if a.json:
        print(json.dumps({"source": src, "blocks": len(blocks), "nodes": nodes,
                          "findings": [{"level": l, "where": w, "message": m} for l, w, m in findings]}, indent=2))
        return 0
    print(f"{src}: {len(blocks)} JSON-LD block(s), {len(nodes)} node(s)")
    for w, t in nodes:
        print(f"  {w}: {', '.join(t)}")
    order = {"error": 0, "warning": 1, "note": 2}
    for level, w, m in sorted(findings, key=lambda f: order[f[0]]):
        print(f"{level.upper():8} {w}: {m}")
    if not any(f[0] == "error" for f in findings):
        print("No errors against the rules this script knows. Check new types in Google's Rich Results Test.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
