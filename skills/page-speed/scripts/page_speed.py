#!/usr/bin/env python3
"""Core Web Vitals and page speed for one page, from Google's PageSpeed Insights or a Lighthouse report.

Usage:
    python3 page_speed.py https://example.com/pricing                 mobile, through the PageSpeed Insights API
    python3 page_speed.py https://example.com/pricing --strategy desktop
    python3 page_speed.py --file report.json                          a Lighthouse or PageSpeed Insights JSON file
    Add --json for machine output.

The API works without a key at low volume, but the shared quota is often used up (it answers 429). Then set a free key
of your own in PAGESPEED_API_KEY (Google Cloud console, enable the PageSpeed Insights API, create an API key), or run
Lighthouse on your machine and pass its report:
    npx lighthouse https://example.com --only-categories=performance --output=json --output-path=report.json \\
        --chrome-flags="--headless"

It reports field data (how real Chrome users experienced the page, at the 75th percentile, when Google has enough of
it), lab data (one Lighthouse run), and the opportunities Lighthouse lists with their estimated savings. The key, if
any, is sent only to googleapis.com and never printed. Standard library only.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

API = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
# Thresholds for "good" and "poor" at the 75th percentile (web.dev, "Web Vitals", updated 31 October 2024).
CWV = {
    "LARGEST_CONTENTFUL_PAINT_MS": ("LCP", "ms", 2500, 4000),
    "INTERACTION_TO_NEXT_PAINT": ("INP", "ms", 200, 500),
    "CUMULATIVE_LAYOUT_SHIFT_SCORE": ("CLS", "", 0.1, 0.25),
    "FIRST_CONTENTFUL_PAINT_MS": ("FCP", "ms", 1800, 3000),
    "EXPERIMENTAL_TIME_TO_FIRST_BYTE": ("TTFB", "ms", 800, 1800),
}
LAB = [("largest-contentful-paint", "LCP"), ("total-blocking-time", "TBT"), ("cumulative-layout-shift", "CLS"),
       ("first-contentful-paint", "FCP"), ("speed-index", "Speed Index"), ("server-response-time", "Server response")]


def fetch_psi(url, strategy, key=None):
    q = {"url": url, "strategy": strategy, "category": "performance"}
    if key:
        q["key"] = key
    req = urllib.request.Request(API + "?" + urllib.parse.urlencode(q), headers={"User-Agent": "VisibianSkill/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.load(r), None
    except urllib.error.HTTPError as e:
        try:
            msg = json.load(e).get("error", {}).get("message", "")
        except Exception:
            msg = ""
        if e.code == 429:
            return None, ("PageSpeed Insights answered 429: the shared quota is used up. Set PAGESPEED_API_KEY to a "
                          "free key of your own, or run Lighthouse locally and pass --file (see --help).")
        return None, f"PageSpeed Insights answered {e.code}: {msg[:300]}"
    except Exception as e:
        return None, f"could not reach PageSpeed Insights: {type(e).__name__}: {e}"


def category(value, good, poor):
    return "good" if value <= good else "poor" if value > poor else "needs improvement"


def field(block):
    out = []
    for key, (name, unit, good, poor) in CWV.items():
        m = (block or {}).get("metrics", {}).get(key)
        if not m or "percentile" not in m:
            continue
        v = m["percentile"] / 100 if name == "CLS" else m["percentile"]
        out.append({"metric": name, "p75": v, "unit": unit, "category": category(v, good, poor),
                    "google_category": m.get("category")})
    return out


def first_node(details):
    """The first element node in Lighthouse details, which nest differently between versions."""
    stack = [details]
    while stack:
        x = stack.pop(0)
        if isinstance(x, dict):
            if isinstance(x.get("node"), dict):
                return x["node"].get("snippet") or x["node"].get("nodeLabel")
            stack += list(x.values())
        elif isinstance(x, list):
            stack += x
    return None


def parse(data):
    lh = data.get("lighthouseResult", data)   # a PSI answer wraps the Lighthouse result; a Lighthouse file is it
    audits = lh.get("audits", {})
    lab = []
    for aid, name in LAB:
        a = audits.get(aid)
        if a and a.get("numericValue") is not None:
            lab.append({"metric": name, "value": a["numericValue"], "display": a.get("displayValue", "")})
    opps = []
    for aid, a in audits.items():
        d = a.get("details") or {}
        saving = d.get("overallSavingsMs") or (a.get("metricSavings") or {}).get("LCP")
        if d.get("type") == "opportunity" and saving and (a.get("score") is None or a["score"] < 0.9):
            opps.append({"id": aid, "title": a.get("title"), "saving_ms": round(saving),
                         "bytes": d.get("overallSavingsBytes")})
    opps.sort(key=lambda o: -o["saving_ms"])
    lcp_el = first_node(audits.get("largest-contentful-paint-element", {}).get("details"))
    perf = (lh.get("categories", {}).get("performance") or {}).get("score")
    return {
        "url": lh.get("finalDisplayedUrl") or lh.get("finalUrl") or lh.get("requestedUrl") or data.get("id"),
        "fetched": lh.get("fetchTime"),
        "form_factor": (lh.get("configSettings") or {}).get("formFactor"),
        "lighthouse": lh.get("lighthouseVersion"),
        "performance_score": round(perf * 100) if isinstance(perf, (int, float)) else None,
        # page-level field data, unless Google fell back to the whole site's data
        "field_page": [] if (data.get("loadingExperience") or {}).get("origin_fallback") else
        field(data.get("loadingExperience")),
        "field_origin": field(data.get("originLoadingExperience")),
        "lab": lab,
        "opportunities": opps[:10],
        "lcp_element": lcp_el,
    }


def fmt(v, unit):
    return f"{v / 1000:.1f} s" if unit == "ms" and v >= 1000 else f"{v:.0f} ms" if unit == "ms" else f"{v:.2f}"


def render(r):
    L = [f"# Page speed: {r['url']}", "",
         f"- Measured: {r['fetched'] or 'unknown'}, {r['form_factor'] or 'device not stated'}, Lighthouse "
         f"{r['lighthouse'] or 'version not stated'}"]
    if r["performance_score"] is not None:
        L.append(f"- Lighthouse performance score: {r['performance_score']} (Lighthouse's own score for this one lab "
                 f"run; it moves between runs)")
    for title, rows in (("Field data for this page (real Chrome users, 75th percentile)", r["field_page"]),
                        ("Field data for the whole site", r["field_origin"])):
        L += ["", f"## {title}", ""]
        L += [f"- {x['metric']}: {fmt(x['p75'], x['unit'])} ({x['category']})" for x in rows] or \
             ["- not available: Google has too little data for this page or site, or the source is a local "
              "Lighthouse run"]
    L += ["", "## Lab data (one run)", ""]
    L += [f"- {x['metric']}: {x['display'] or x['value']}" for x in r["lab"]] or ["- none"]
    if r["lcp_element"]:
        L += ["", f"Largest element painted: `{r['lcp_element'][:200]}`"]
    L += ["", "## Opportunities Lighthouse lists", ""]
    L += [f"- {o['title']}: about {o['saving_ms']} ms" + (f", {o['bytes'] // 1024} KiB" if o.get('bytes') else "")
          for o in r["opportunities"]] or ["- none above the threshold"]
    L += ["", "Core Web Vitals thresholds at the 75th percentile: LCP 2.5 s, INP 200 ms, CLS 0.1 (web.dev, \"Web "
              "Vitals\", updated 31 October 2024). Field data decides whether a page passes; lab data helps find why."]
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("url", nargs="?")
    ap.add_argument("--strategy", choices=["mobile", "desktop"], default="mobile")
    ap.add_argument("--file")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if a.file:
        with open(a.file, encoding="utf-8") as f:
            data = json.load(f)
    elif a.url:
        url = a.url if "://" in a.url else "https://" + a.url
        data, err = fetch_psi(url, a.strategy, os.environ.get("PAGESPEED_API_KEY"))
        if err:
            print(err, file=sys.stderr)
            return 2
    else:
        ap.error("give a URL or --file")
    r = parse(data)
    print(json.dumps(r, indent=1) if a.json else render(r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
