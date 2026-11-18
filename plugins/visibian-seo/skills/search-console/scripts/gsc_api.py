#!/usr/bin/env python3
"""Live Google Search Console data through its API: performance rows, URL inspection and sitemaps.

Usage:
    python3 gsc_api.py sites                                  the properties the token can read
    python3 gsc_api.py performance SITE                       last 28 days of query and page rows, to a CSV
    python3 gsc_api.py performance SITE --days 90 --dimensions query --out queries.csv
    python3 gsc_api.py performance SITE --start 2026-08-01 --end 2026-08-31 --type image
    python3 gsc_api.py inspect SITE https://example.com/a https://example.com/b     index status of each page
    python3 gsc_api.py inspect SITE --urls pages.txt          one address per line
    python3 gsc_api.py sitemaps SITE                          submitted sitemaps, with their errors and warnings
    Add --json for machine output.

SITE is the property as Search Console names it: sc-domain:example.com for a domain property, or
https://www.example.com/ for a URL-prefix property ("sites" lists them).

The performance CSV has the columns query, page, clicks, impressions, ctr and position, which the keyword-research
skill's gsc_queries.py reads as it is. The API returns the top rows, not always every row, up to 25,000 a request;
this script pages through them up to --max-rows (Google, "Search Analytics: query", read 17 November 2026).

URL inspection is limited to 2,000 requests a day and 600 a minute for each property (Google, "Usage limits", read
17 November 2026), so --max caps a run at 100 pages unless raised.

Needs an OAuth access token with the scope https://www.googleapis.com/auth/webmasters.readonly, for a Google account
that can see the property, in the environment variable SEARCH_CONSOLE_TOKEN. Two ways to get one:
  - Google's OAuth 2.0 Playground (developers.google.com/oauthplayground): choose Search Console API v3, the
    webmasters.readonly scope, authorize, exchange the code, and copy the access token. It lasts one hour.
  - gcloud: gcloud auth application-default login --scopes=https://www.googleapis.com/auth/webmasters.readonly,\\
    https://www.googleapis.com/auth/cloud-platform, then SEARCH_CONSOLE_TOKEN=$(gcloud auth application-default
    print-access-token).
The token is sent only to searchconsole.googleapis.com and never printed. Standard library only.
"""
import argparse
import csv
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

API = "https://searchconsole.googleapis.com"
SCOPE = "https://www.googleapis.com/auth/webmasters.readonly"
PAGE_ROWS = 25000
TYPES = ["web", "image", "video", "news", "discover", "googleNews"]
DIMENSIONS = ["query", "page", "country", "device", "date", "searchAppearance"]


class ApiError(Exception):
    pass


def call(method, path, token, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(API + path, data=data, method=method, headers={
        "Authorization": "Bearer " + token, "Content-Type": "application/json", "User-Agent": "VisibianSkill/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        try:
            msg = json.load(e).get("error", {}).get("message", "")
        except Exception:
            msg = ""
        e.close()
        hint = {401: "The token is missing, wrong or expired (tokens from the OAuth Playground last one hour).",
                403: f"The token's account cannot read this property, or the token lacks the scope {SCOPE}.",
                404: "Search Console does not know this property. Check its exact name with: gsc_api.py sites",
                429: "The quota is used up for now. Wait, or inspect fewer pages."}.get(e.code, "")
        raise ApiError(f"Search Console answered {e.code}. {hint} {msg[:300]}".strip())
    except urllib.error.URLError as e:
        raise ApiError(f"could not reach Search Console: {e.reason}")


def site_path(site):
    return "/webmasters/v3/sites/" + urllib.parse.quote(site, safe="")


def sites(token):
    return [{"site": s.get("siteUrl"), "permission": s.get("permissionLevel")}
            for s in call("GET", "/webmasters/v3/sites", token).get("siteEntry", [])]


def dates(days, start, end, today=None):
    """Search Console's data trails by two or three days, so the window ends three days ago unless --end is given."""
    today = today or dt.date.today()
    end_d = dt.date.fromisoformat(end) if end else today - dt.timedelta(days=3)
    start_d = dt.date.fromisoformat(start) if start else end_d - dt.timedelta(days=days - 1)
    if start_d > end_d:
        raise ApiError("the start date is after the end date")
    return start_d.isoformat(), end_d.isoformat()


def performance(token, site, start, end, dimensions, kind="web", max_rows=100000):
    rows, offset = [], 0
    while len(rows) < max_rows:
        body = {"startDate": start, "endDate": end, "dimensions": dimensions, "type": kind,
                "rowLimit": min(PAGE_ROWS, max_rows - len(rows)), "startRow": offset}
        got = call("POST", site_path(site) + "/searchAnalytics/query", token, body).get("rows", [])
        for r in got:
            rec = dict(zip(dimensions, r.get("keys", [])))
            rec.update({"clicks": r.get("clicks", 0), "impressions": r.get("impressions", 0),
                        "ctr": round(r.get("ctr", 0), 6), "position": round(r.get("position", 0), 2)})
            rows.append(rec)
        if len(got) < body["rowLimit"]:
            break
        offset += len(got)
    return rows


def write_csv(rows, dimensions, path):
    cols = dimensions + ["clicks", "impressions", "ctr", "position"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)


def inspect(token, site, url):
    body = {"inspectionUrl": url, "siteUrl": site, "languageCode": "en-US"}
    res = call("POST", "/v1/urlInspection/index:inspect", token, body).get("inspectionResult", {})
    ix = res.get("indexStatusResult", {})
    rich = res.get("richResultsResult", {})
    issues = [f"{i.get('severity', '').lower()}: {i.get('issueMessage', '')}"
              for d in rich.get("detectedItems", []) for it in d.get("items", []) for i in it.get("issues", [])]
    return {"url": url, "verdict": ix.get("verdict"), "coverage": ix.get("coverageState"),
            "indexing": ix.get("indexingState"), "robots_txt": ix.get("robotsTxtState"),
            "fetch": ix.get("pageFetchState"), "last_crawl": ix.get("lastCrawlTime"),
            "crawled_as": ix.get("crawledAs"), "google_canonical": ix.get("googleCanonical"),
            "user_canonical": ix.get("userCanonical"), "sitemaps": ix.get("sitemap", []),
            "referring": ix.get("referringUrls", []),
            "rich_results": [d.get("richResultType") for d in rich.get("detectedItems", [])],
            "rich_issues": issues, "link": res.get("inspectionResultLink")}


def problems(r, today=None):
    """What a person should look at for one inspected page; observed facts only."""
    out = []
    if r["verdict"] not in ("PASS", None):
        out.append(f"not indexed: {r['coverage'] or r['verdict']}")
    if r["indexing"] and r["indexing"] != "INDEXING_ALLOWED":
        out.append(f"indexing blocked ({r['indexing']})")
    if r["robots_txt"] == "DISALLOWED":
        out.append("robots.txt disallows it")
    if r["fetch"] and r["fetch"] != "SUCCESSFUL":
        out.append(f"Google's last fetch: {r['fetch']}")
    if r["google_canonical"] and r["user_canonical"] and r["google_canonical"] != r["user_canonical"]:
        out.append(f"Google chose another canonical: {r['google_canonical']}")
    if r["last_crawl"]:
        try:
            seen = dt.datetime.fromisoformat(r["last_crawl"].replace("Z", "+00:00")).date()
            age = ((today or dt.date.today()) - seen).days
            if age > 90:
                out.append(f"last crawled {age} days ago")
        except ValueError:
            pass
    out += r["rich_issues"]
    return out


def sitemaps(token, site):
    out = []
    for s in call("GET", site_path(site) + "/sitemaps", token).get("sitemap", []):
        submitted = sum(int(c.get("submitted", 0) or 0) for c in s.get("contents", []))
        out.append({"path": s.get("path"), "last_downloaded": s.get("lastDownloaded"),
                    "pending": s.get("isPending"), "index": s.get("isSitemapsIndex"),
                    "errors": int(s.get("errors", 0) or 0), "warnings": int(s.get("warnings", 0) or 0),
                    "submitted": submitted})
    return out


def table(head, rows):
    esc = lambda v: str("" if v is None else v).replace("|", "\\|")
    return "\n".join(["| " + " | ".join(head) + " |", "|" + "---|" * len(head)] +
                     ["| " + " | ".join(esc(v) for v in r) + " |" for r in rows])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("sites")
    p = sub.add_parser("performance")
    p.add_argument("site")
    p.add_argument("--days", type=int, default=28)
    p.add_argument("--start")
    p.add_argument("--end")
    p.add_argument("--dimensions", default="query,page")
    p.add_argument("--type", default="web", choices=TYPES)
    p.add_argument("--max-rows", type=int, default=100000)
    p.add_argument("--out", default="search-console-performance.csv")
    i = sub.add_parser("inspect")
    i.add_argument("site")
    i.add_argument("urls", nargs="*")
    i.add_argument("--urls", dest="url_file")
    i.add_argument("--max", type=int, default=100)
    s = sub.add_parser("sitemaps")
    s.add_argument("site")
    for x in (p, i, s):
        x.add_argument("--json", action="store_true")
    sub.choices["sites"].add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    token = os.environ.get("SEARCH_CONSOLE_TOKEN", "").strip()
    if not token:
        print("Set SEARCH_CONSOLE_TOKEN to an OAuth access token with the webmasters.readonly scope (see --help). "
              "Without one, use the Performance export from Search Console with the keyword-research skill.",
              file=sys.stderr)
        return 2
    try:
        if a.cmd == "sites":
            got = sites(token)
            print(json.dumps(got, indent=1) if a.json else
                  table(["Property", "Permission"], [(g["site"], g["permission"]) for g in got]))
        elif a.cmd == "performance":
            dims = [d.strip() for d in a.dimensions.split(",") if d.strip()]
            bad = [d for d in dims if d not in DIMENSIONS]
            if bad:
                print(f"unknown dimension {', '.join(bad)}; use {', '.join(DIMENSIONS)}", file=sys.stderr)
                return 2
            start, end = dates(a.days, a.start, a.end)
            rows = performance(token, a.site, start, end, dims, a.type, a.max_rows)
            write_csv(rows, dims, a.out)
            clicks, imps = sum(r["clicks"] for r in rows), sum(r["impressions"] for r in rows)
            summary = {"site": a.site, "type": a.type, "start": start, "end": end, "dimensions": dims,
                       "rows": len(rows), "clicks": clicks, "impressions": imps, "csv": a.out}
            print(json.dumps(summary, indent=1) if a.json else
                  f"{a.site}, {a.type} search, {start} to {end} (Pacific time): {len(rows):,} rows by "
                  f"{' and '.join(dims)}, {clicks:,.0f} clicks, {imps:,.0f} impressions.\nWritten to {a.out}. "
                  f"Next: python3 gsc_queries.py {a.out} (the keyword-research skill).")
        elif a.cmd == "inspect":
            urls = list(a.urls)
            if a.url_file:
                with open(a.url_file, encoding="utf-8") as f:
                    urls += [l.strip() for l in f if l.strip() and not l.startswith("#")]
            urls = list(dict.fromkeys(urls))
            if not urls:
                print("give one or more page addresses, or --urls FILE", file=sys.stderr)
                return 2
            if len(urls) > a.max:
                print(f"{len(urls)} pages given; inspecting the first {a.max} (--max). The quota is 2,000 a day "
                      f"for each property.", file=sys.stderr)
                urls = urls[:a.max]
            res = [inspect(token, a.site, u) for u in urls]
            for r in res:
                r["problems"] = problems(r)
            if a.json:
                print(json.dumps(res, indent=1))
            else:
                bad = [r for r in res if r["problems"]]
                print(f"# URL inspection, {a.site}\n\n{len(res)} pages inspected; {len(bad)} with something to "
                      f"look at.\n")
                print(table(["Page", "Coverage", "Last crawl", "Crawled as", "To look at"],
                            [(r["url"], r["coverage"], (r["last_crawl"] or "")[:10], r["crawled_as"],
                              "; ".join(r["problems"]) or "nothing") for r in res]))
        elif a.cmd == "sitemaps":
            res = sitemaps(token, a.site)
            print(json.dumps(res, indent=1) if a.json else
                  (table(["Sitemap", "Addresses", "Errors", "Warnings", "Last read by Google", "Pending"],
                         [(r["path"], r["submitted"], r["errors"], r["warnings"], (r["last_downloaded"] or "")[:10],
                           "yes" if r["pending"] else "") for r in res]) if res else
                   "No sitemaps are submitted for this property."))
    except ApiError as e:
        print(str(e), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
