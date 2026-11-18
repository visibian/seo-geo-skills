#!/usr/bin/env python3
"""Compare the identity facts a brand states on its own pages.

Usage:
    python3 facts_across_pages.py https://example.com https://example.com/about https://example.com/contact
    python3 facts_across_pages.py --file urls.txt          one URL per line
    Add --json for machine output.

For each page it reads, from the raw HTML: the Organization or LocalBusiness structured data (name, legal name,
description, URL, logo, sameAs, address, telephone, email, founding date), og:site_name, telephone and email links,
and the page title. It then lists every fact that differs between pages. It reads only the pages given, once each,
identified as VisibianSkill/1.0.

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
ORG_TYPES = {"Organization", "Corporation", "LocalBusiness", "OnlineBusiness", "OnlineStore", "ProfessionalService",
             "LegalService", "Dentist", "MedicalBusiness", "Store", "Restaurant", "NGO", "EducationalOrganization"}
FIELDS = ["name", "legalName", "alternateName", "description", "url", "logo", "telephone", "email", "foundingDate",
          "address", "sameAs"]


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read(3 * 1024 * 1024).decode("utf-8", "replace")


def norm(v):
    if isinstance(v, dict):
        if v.get("@type") == "PostalAddress" or "streetAddress" in v:
            parts = [v.get(k) for k in ("streetAddress", "addressLocality", "addressRegion", "postalCode",
                                        "addressCountry")]
            return ", ".join(str(p if not isinstance(p, dict) else p.get("name", "")) for p in parts if p)
        return v.get("name") or v.get("url") or v.get("@id") or json.dumps(v, sort_keys=True)
    if isinstance(v, list):
        return " | ".join(sorted(norm(x) for x in v))
    return re.sub(r"\s+", " ", html.unescape(str(v))).strip()


def org_nodes(doc):
    out = []
    for raw in re.findall(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', doc, re.S | re.I):
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        stack = [data]
        while stack:
            x = stack.pop()
            if isinstance(x, dict):
                t = x.get("@type")
                ts = {t} if isinstance(t, str) else set(t or [])
                if ts & ORG_TYPES:
                    out.append(x)
                stack += list(x.values())
            elif isinstance(x, list):
                stack += x
    return out


def facts(doc):
    f = {}
    for node in org_nodes(doc):
        for k in FIELDS:
            if k in node and k not in f:
                f[k] = norm(node[k])
    m = re.search(r'<meta[^>]+property=["\']og:site_name["\'][^>]+content=["\']([^"\']*)', doc, re.I)
    if m:
        f["og:site_name"] = norm(m.group(1))
    t = re.search(r"<title[^>]*>(.*?)</title>", doc, re.S | re.I)
    if t:
        f["title"] = norm(re.sub(r"<[^>]+>", "", t.group(1)))
    tels = sorted({re.sub(r"[^\d+]", "", x) for x in re.findall(r'href=["\']tel:([^"\']+)', doc, re.I)})
    mails = sorted({x.lower() for x in re.findall(r'href=["\']mailto:([^"\'?]+)', doc, re.I)})
    if tels:
        f["telephone links"] = " | ".join(tels)
    if mails:
        f["email links"] = " | ".join(mails)
    return f


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("urls", nargs="*")
    ap.add_argument("--file")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    urls = list(a.urls)
    if a.file:
        urls += [l.strip() for l in pathlib.Path(a.file).read_text().splitlines() if l.strip()]
    if not urls:
        ap.error("give at least one URL")
    pages = {}
    for u in urls:
        u = u if "://" in u else "https://" + u
        try:
            pages[u] = facts(fetch(u))
        except Exception as e:
            pages[u] = {"error": f"{type(e).__name__}: {e}"}
    keys = sorted({k for f in pages.values() for k in f if k not in ("error", "title")})
    differs = {}
    for k in keys:
        vals = {u: f[k] for u, f in pages.items() if k in f}
        if len(set(vals.values())) > 1:
            differs[k] = vals
    if a.json:
        print(json.dumps({"pages": pages, "differs": differs}, indent=2, ensure_ascii=False))
        return 0
    for u, f in pages.items():
        print(f"\n{u}")
        for k, v in f.items():
            print(f"  {k}: {v}")
    print("\nFacts that differ between pages:" if differs else "\nNo fact differs between the pages read.")
    for k, vals in differs.items():
        print(f"- {k}")
        for u, v in vals.items():
            print(f"    {u}: {v}")
    readable = [u for u, f in pages.items() if "error" not in f]
    partial = [k for k in keys if 0 < sum(k in pages[u] for u in readable) < len(readable)]
    if partial:
        print("\nStated on some pages and not on others (often fine, worth a look): " + ", ".join(partial))
    missing = [k for k in ("name", "description", "url", "logo", "sameAs") if not any(k in f for f in pages.values())]
    if missing:
        print("\nNot stated in structured data on any page read: " + ", ".join(missing))
    return 0


if __name__ == "__main__":
    sys.exit(main())
