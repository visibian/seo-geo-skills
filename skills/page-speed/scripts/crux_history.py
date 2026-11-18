#!/usr/bin/env python3
"""Real-user Core Web Vitals over time, for a whole site or one page, from Google's Chrome UX Report (CrUX).

Usage:
    python3 crux_history.py https://example.com                  the whole site (the origin), all devices
    python3 crux_history.py https://example.com/pricing --page   that page only
    python3 crux_history.py https://example.com --form-factor phone --periods 40
    python3 crux_history.py --file history.json                  a saved CrUX API answer
    Add --json for machine output.

It asks the CrUX History API, which returns weekly collection periods, each a rolling 28 days of real Chrome visits:
25 by default, up to 40 (Chrome for Developers, "CrUX History API", read 17 November 2026). The newest period is the
site's current state; the others show whether a change worked.

Needs a free Google API key with the Chrome UX Report API enabled, in CRUX_API_KEY (or PAGESPEED_API_KEY, if the same
key has both APIs): Google Cloud console, APIs and services, enable "Chrome UX Report API", create an API key. The key
is sent only to chromeuxreport.googleapis.com and never printed. Standard library only.
"""
import argparse
import datetime as dt
import json
import math
import os
import sys
import urllib.error
import urllib.request

API = "https://chromeuxreport.googleapis.com/v1/records:queryHistoryRecord"
# Thresholds for "good" and "poor" at the 75th percentile, as page_speed.py uses them (web.dev, "Web Vitals", updated
# 31 October 2024, and its pages on FCP and TTFB).
METRICS = {
    "largest_contentful_paint": ("LCP", "ms", 2500, 4000, True),
    "interaction_to_next_paint": ("INP", "ms", 200, 500, True),
    "cumulative_layout_shift": ("CLS", "", 0.1, 0.25, True),
    "first_contentful_paint": ("FCP", "ms", 1800, 3000, False),
    "experimental_time_to_first_byte": ("TTFB", "ms", 800, 1800, False),
}
FACTORS = {"all": None, "phone": "PHONE", "desktop": "DESKTOP", "tablet": "TABLET"}


def fetch(target, page, factor, periods, key):
    body = {("url" if page else "origin"): target, "collectionPeriodCount": periods}
    if FACTORS[factor]:
        body["formFactor"] = FACTORS[factor]
    req = urllib.request.Request(API + "?key=" + key, data=json.dumps(body).encode(), method="POST",
                                 headers={"Content-Type": "application/json", "User-Agent": "VisibianSkill/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r), None
    except urllib.error.HTTPError as e:
        try:
            msg = json.load(e).get("error", {}).get("message", "")
        except Exception:
            msg = ""
        if e.code == 404:
            return None, ("CrUX has no data for this " + ("page" if page else "site") + ": not enough Chrome users "
                          "visited it in the period. Try the whole site (drop --page), or use lab data from "
                          "page_speed.py.")
        return None, f"the Chrome UX Report API answered {e.code}: {msg[:300]}"
    except urllib.error.URLError as e:
        return None, f"could not reach the Chrome UX Report API: {e.reason}"


def number(v):
    """CrUX writes CLS as a string, and a missing week as null (percentiles) or "NaN" (densities)."""
    if v is None:
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(f) else f


def day(d):
    return dt.date(d["year"], d["month"], d["day"]) if d else None


def rating(v, good, poor):
    return None if v is None else "good" if v <= good else "poor" if v > poor else "needs improvement"


def parse(data):
    rec = data.get("record", data)
    key = rec.get("key", {})
    periods = [(day(p.get("firstDate")), day(p.get("lastDate"))) for p in rec.get("collectionPeriods", [])]
    out = []
    for name, m in rec.get("metrics", {}).items():
        if name not in METRICS:
            continue
        label, unit, good, poor, core = METRICS[name]
        p75s = [number(v) for v in m.get("percentilesTimeseries", {}).get("p75s", [])]
        hist = m.get("histogramTimeseries", [])
        good_share = [number(v) for v in hist[0].get("densities", [])] if hist else []
        known = [(i, v) for i, v in enumerate(p75s) if v is not None]
        if not known:
            continue
        first_i, first = known[0]
        last_i, last = known[-1]
        good_weeks = sum(1 for _, v in known if v <= good)
        out.append({"metric": label, "unit": unit, "core": core, "p75": last, "rating": rating(last, good, poor),
                    "good_share": good_share[last_i] if last_i < len(good_share) else None,
                    "first_p75": first, "first_rating": rating(first, good, poor),
                    "first_period_end": periods[first_i][1].isoformat() if first_i < len(periods) else None,
                    "best": min(v for _, v in known), "worst": max(v for _, v in known),
                    "periods_with_data": len(known), "periods_good": good_weeks,
                    "change": last - first, "series": p75s})
    order = list(m[0] for m in METRICS.values())
    out.sort(key=lambda r: order.index(r["metric"]))
    latest = periods[-1] if periods else (None, None)
    return {"target": key.get("origin") or key.get("url"), "page": "url" in key,
            "form_factor": (key.get("formFactor") or "ALL").lower(), "periods": len(periods),
            "latest_start": latest[0].isoformat() if latest[0] else None,
            "latest_end": latest[1].isoformat() if latest[1] else None,
            "since": periods[0][0].isoformat() if periods and periods[0][0] else None, "metrics": out}


def fmt(v, unit):
    if v is None:
        return "no data"
    return f"{v:.2f}" if not unit else f"{v / 1000:.2f} s" if v >= 1000 else f"{v:.0f} ms"


def verdict(r):
    core = [m for m in r["metrics"] if m["core"]]
    if len(core) < 3:
        return "Not every Core Web Vital has data, so no pass or fail."
    passed = all(m["rating"] == "good" for m in core)
    return ("All three Core Web Vitals are good at the 75th percentile." if passed else
            "Core Web Vitals not passed: " + ", ".join(f"{m['metric']} is {m['rating']}" for m in core
                                                      if m["rating"] != "good") + ".")


def render(r):
    kind = "page" if r["page"] else "whole site"
    lines = [f"# Chrome UX Report: {r['target']} ({kind}, {r['form_factor']} devices)", "",
             f"Latest period: {r['latest_start']} to {r['latest_end']}, real Chrome visits. History: {r['periods']} "
             f"weekly periods since {r['since']}.", "", verdict(r), "",
             "| Metric | Now (p75) | Rating | Visits with a good experience | First in history | Best | Worst | "
             "Periods good |", "|---|---|---|---|---|---|---|---|"]
    for m in r["metrics"]:
        share = f"{m['good_share'] * 100:.0f}%" if m["good_share"] is not None else ""
        lines.append(f"| {m['metric']} | {fmt(m['p75'], m['unit'])} | {m['rating']} | {share} | "
                     f"{fmt(m['first_p75'], m['unit'])} ({m['first_rating']}) | {fmt(m['best'], m['unit'])} | "
                     f"{fmt(m['worst'], m['unit'])} | {m['periods_good']} of {m['periods_with_data']} |")
    moved = [m for m in r["metrics"] if m["first_rating"] != m["rating"]]
    if moved:
        lines += ["", "Changed over the history: " + "; ".join(
            f"{m['metric']} from {m['first_rating']} to {m['rating']}" for m in moved) + "."]
    lines += ["", "Each period is the 28 days before its end date, so a fix shows fully about four weeks after it "
              "ships."]
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("url", nargs="?")
    ap.add_argument("--page", action="store_true", help="that page only, not the whole site")
    ap.add_argument("--form-factor", choices=list(FACTORS), default="all")
    ap.add_argument("--periods", type=int, default=25)
    ap.add_argument("--file")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if a.file:
        with open(a.file, encoding="utf-8") as f:
            data = json.load(f)
    else:
        if not a.url:
            ap.error("give a URL or --file")
        key = os.environ.get("CRUX_API_KEY") or os.environ.get("PAGESPEED_API_KEY")
        if not key:
            print("Set CRUX_API_KEY to a free Google API key with the Chrome UX Report API enabled (see --help). "
                  "Without one, page_speed.py shows the latest field data from PageSpeed Insights.", file=sys.stderr)
            return 2
        url = a.url if "://" in a.url else "https://" + a.url
        target = url if a.page else "/".join(url.split("/")[:3])
        data, err = fetch(target, a.page, a.form_factor, max(1, min(a.periods, 40)), key)
        if err:
            print(err, file=sys.stderr)
            return 1
    r = parse(data)
    print(json.dumps({k: v for k, v in r.items()}, indent=1) if a.json else render(r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
