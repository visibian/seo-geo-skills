#!/usr/bin/env python3
"""A client-ready SEO and AI search report, as one HTML file, from a seo-audit crawl and optional page speed results.

Usage:
    python3 make_report.py seo-audit/audit.json --client "Acme" --by "Your Agency" --out report.html
    python3 make_report.py seo-audit/audit.json --speed speed-home.json --speed speed-pricing.json ...
    --logo logo.png       your logo, embedded in the file (PNG, JPEG or SVG)
    --notes notes.md      your own summary and recommendations, placed first (plain text or simple Markdown)
    --no-credit           leave out the small line naming the tool that made the report

The speed files are page_speed.py --json output. The report holds only what the audit observed and the notes you add;
it invents no score. Open it in a browser and print to PDF to send it. Standard library only.
"""
import argparse
import base64
import collections
import datetime
import html
import json
import mimetypes
import pathlib
import re
import sys
import urllib.parse

LEVEL = {"blocker": "Fix first", "fix": "Fix", "suggestion": "Worth doing"}
CSS = """
:root{--ink:#16181d;--sub:#5b6170;--line:#e4e6eb;--soft:#f6f7f9;--accent:#1f4fd8;--bad:#b42318;--mid:#b54708;--ok:#067647}
*{box-sizing:border-box}body{margin:0;font:15px/1.55 -apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;color:var(--ink)}
main{max-width:920px;margin:0 auto;padding:48px 32px}
header{display:flex;justify-content:space-between;align-items:flex-start;gap:24px;border-bottom:2px solid var(--ink);padding-bottom:20px}
header img{max-height:56px;max-width:200px}h1{font-size:30px;line-height:1.15;margin:0 0 6px;letter-spacing:-.01em}
.meta{color:var(--sub);font-size:14px}h2{font-size:20px;margin:40px 0 12px;padding-top:8px;border-top:1px solid var(--line)}
h3{font-size:16px;margin:22px 0 6px}.cards{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:24px 0}
.card{border:1px solid var(--line);border-radius:8px;padding:14px}.card b{display:block;font-size:26px;line-height:1.1}
.card span{color:var(--sub);font-size:13px}.blocker b{color:var(--bad)}.fix b{color:var(--mid)}.suggestion b{color:var(--accent)}
.item{border-left:3px solid var(--line);padding:4px 0 4px 14px;margin:14px 0}.item.blocker{border-color:var(--bad)}
.item.fix{border-color:var(--mid)}.item.suggestion{border-color:var(--accent)}.item p{margin:2px 0}
.cat{font-size:12px;text-transform:uppercase;letter-spacing:.06em;color:var(--sub)}
details{margin:4px 0}summary{cursor:pointer;color:var(--sub);font-size:13px}
ul.urls{margin:6px 0;padding-left:18px;font-size:13px;word-break:break-all}
table{width:100%;border-collapse:collapse;font-size:13px;margin:8px 0}th,td{text-align:left;padding:6px 8px;border-bottom:1px solid var(--line);vertical-align:top}
th{background:var(--soft);font-weight:600}td.url{word-break:break-all}.notes{background:var(--soft);border-radius:8px;padding:16px 20px}
footer{margin-top:48px;color:var(--sub);font-size:12px;border-top:1px solid var(--line);padding-top:12px}
@media print{main{padding:0}h2{break-after:avoid}.item,tr{break-inside:avoid}details{display:block}details>ul{display:block}}
@media (max-width:700px){.cards{grid-template-columns:repeat(2,1fr)}}
"""


def esc(x):
    return html.escape(str(x if x is not None else ""))


def md(text):
    """Very small Markdown: paragraphs, bullet lists, **bold**, headings."""
    out, lst = [], False
    for line in text.splitlines():
        s = line.strip()
        if s.startswith(("- ", "* ")):
            if not lst:
                out.append("<ul>")
                lst = True
            out.append(f"<li>{inline(s[2:])}</li>")
            continue
        if lst:
            out.append("</ul>")
            lst = False
        if s.startswith("#"):
            out.append(f"<h3>{inline(s.lstrip('#').strip())}</h3>")
        elif s:
            out.append(f"<p>{inline(s)}</p>")
    if lst:
        out.append("</ul>")
    return "\n".join(out)


def inline(s):
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", esc(s))


def logo_tag(path):
    if not path:
        return ""
    p = pathlib.Path(path)
    mime = mimetypes.guess_type(p.name)[0] or "image/png"
    return f'<img alt="" src="data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}">'


def speed_rows(files):
    rows = []
    for f in files:
        d = json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
        field = {x["metric"]: x for x in d.get("field_page") or d.get("field_origin") or []}
        lab = {x["metric"]: x for x in d.get("lab", [])}
        cell = lambda m: (f"{field[m]['p75']:.2f} ({field[m]['category']})" if m == "CLS" else
                          f"{field[m]['p75'] / 1000:.1f} s ({field[m]['category']})" if m == "LCP" else
                          f"{field[m]['p75']:.0f} ms ({field[m]['category']})") if m in field else "no field data"
        rows.append((d.get("url"), d.get("form_factor"), cell("LCP"), cell("INP"), cell("CLS"),
                     lab.get("LCP", {}).get("display", "")))
    return rows


def build(audit, client, by, logo, notes, speed, credit):
    pages = audit["pages"]
    site = urllib.parse.urlsplit(audit["site"]).netloc
    found = audit.get("findings", [])
    count = collections.Counter(f["level"] for f in found)
    html_pages = [p for p in pages.values() if "title" in p]
    per_page = collections.Counter(u for f in found for u in f["urls"])
    H = [f"<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" "
         f"content=\"width=device-width,initial-scale=1\"><title>SEO and AI search report: {esc(client or site)}</title>"
         f"<style>{CSS}</style></head><body><main>",
         f"<header><div><h1>SEO and AI search report</h1><div class=\"meta\">{esc(client or site)} · {esc(site)} · "
         f"crawled {esc(audit.get('checked'))}{' · prepared by ' + esc(by) if by else ''}</div></div>{logo_tag(logo)}</header>"]
    H.append("<div class=\"cards\">" + "".join(
        f"<div class=\"card {c}\"><b>{n}</b><span>{label}</span></div>" for c, n, label in
        (("", len(pages), "pages checked"), ("blocker", count["blocker"], "to fix first"),
         ("fix", count["fix"], "fixes"), ("suggestion", count["suggestion"], "worth doing"))) + "</div>")
    if notes:
        H.append(f"<h2>Summary</h2><div class=\"notes\">{md(notes)}</div>")
    for lvl in ("blocker", "fix", "suggestion"):
        items = [f for f in found if f["level"] == lvl]
        if not items:
            continue
        H.append(f"<h2>{LEVEL[lvl]}</h2>")
        for f in items:
            urls = "".join(f"<li>{esc(u)}</li>" for u in f["urls"][:50])
            more = f"<li>and {len(f['urls']) - 50} more</li>" if len(f["urls"]) > 50 else ""
            H.append(f"<div class=\"item {lvl}\"><div class=\"cat\">{esc(f['category'])}</div><p>{esc(f['message'])}.</p>"
                     + (f"<details><summary>{len(f['urls'])} {'address' if len(f['urls']) == 1 else 'addresses'}</summary><ul class=\"urls\">{urls}{more}</ul>"
                        f"</details>" if f["urls"] else "") + "</div>")
    if speed:
        H.append("<h2>Page speed</h2><table><tr><th>Page</th><th>Device</th><th>LCP</th><th>INP</th><th>CLS</th>"
                 "<th>Lab LCP</th></tr>" + "".join("<tr>" + "".join(f"<td{' class=url' if i == 0 else ''}>{esc(c)}</td>"
                                                                    for i, c in enumerate(r)) + "</tr>"
                                                   for r in speed_rows(speed)) + "</table>"
                 "<p class=\"meta\">Field data at the 75th percentile from real Chrome users where Google has it; "
                 "thresholds LCP 2.5 s, INP 200 ms, CLS 0.1 (web.dev, updated 31 October 2024).</p>")
    shut = [r for r in audit.get("crawlers", []) if r.get("paths") and not all(r["paths"].values())]
    H.append("<h2>Search and AI crawlers</h2><table><tr><th>Crawler</th><th>Company</th><th>Used for</th><th>Kind</th>"
             "<th>Home page</th></tr>" + "".join(
                 f"<tr><td>{esc(r['token'])}</td><td>{esc(r['company'])}</td><td>{esc(r['product'])}</td>"
                 f"<td>{esc(r['kind'])}</td><td>{'open' if all(r['paths'].values()) else 'closed'}</td></tr>"
                 for r in audit.get("crawlers", []) if r.get("paths")) + "</table>"
             f"<p class=\"meta\">{len(shut)} closed by robots.txt. Each crawler's facts from its company's documentation, "
             f"read {esc(audit.get('crawler_facts_read'))}.</p>")
    rows = sorted(html_pages, key=lambda p: (-per_page[p["url"]], p["url"]))
    H.append("<h2>Pages</h2><table><tr><th>Page</th><th>Answer</th><th>Title</th><th>Words</th><th>Findings</th></tr>" +
             "".join(f"<tr><td class=url>{esc(p['url'])}</td><td>{esc(p.get('status'))}</td><td>{esc(p.get('title'))}"
                     f"</td><td>{esc(p.get('words'))}</td><td>{per_page[p['url']]}</td></tr>" for p in rows[:300]) +
             "</table>")
    H.append("<h2>How this was checked</h2><p>The site was crawled from its home page and sitemap the way a search "
             "crawler reads it, without running scripts, respecting robots.txt. Findings are what was observed on the "
             "pages listed. Not covered: links from other sites, rankings and traffic, and what AI assistants say about "
             "the brand, which needs repeated answers across assistants over time.</p>")
    stamp = datetime.date.today().isoformat()
    H.append(f"<footer>Report generated {stamp}." + (" Made with the open-source Visibian SEO &amp; GEO skills, "
             "github.com/visibian/seo-geo-skills." if credit else "") + "</footer></main></body></html>")
    return "\n".join(H)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("audit")
    ap.add_argument("--client", default="")
    ap.add_argument("--by", default="")
    ap.add_argument("--logo")
    ap.add_argument("--notes")
    ap.add_argument("--speed", action="append", default=[])
    ap.add_argument("--no-credit", action="store_true")
    ap.add_argument("--out", default="report.html")
    a = ap.parse_args(argv)
    audit = json.loads(pathlib.Path(a.audit).read_text(encoding="utf-8"))
    notes = pathlib.Path(a.notes).read_text(encoding="utf-8") if a.notes else ""
    out = build(audit, a.client, a.by, a.logo, notes, a.speed, not a.no_credit)
    pathlib.Path(a.out).write_text(out, encoding="utf-8")
    print(f"wrote {a.out} ({len(out):,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
