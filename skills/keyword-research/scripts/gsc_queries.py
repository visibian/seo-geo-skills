#!/usr/bin/env python3
"""Keyword research from a site's own Google Search Console data: quick wins, low click-through, questions, topics.

Usage:
    python3 gsc_queries.py Queries.csv                         the Queries table of a Search Console Performance export
    python3 gsc_queries.py Queries.csv --compare Queries-before.csv   the same table for an earlier period
    python3 gsc_queries.py Queries.csv --brand "acme,acme analytics"  split branded from non-branded queries
    python3 gsc_queries.py pairs.csv                           query and page in one table (from the API, Looker Studio
                                                               or BigQuery): adds pages that compete for one query
    Add --json for machine output, --min-impressions 50 to change the floor (default 20).

Reads the export as Search Console writes it (Top queries, Clicks, Impressions, CTR, Position; CTR such as "3.2%"), or
any CSV with columns named query, page, clicks, impressions, ctr, position. Benchmarks come from the site's own data
(its median click-through at each position), never from an outside average. Standard library only.
"""
import argparse
import collections
import csv
import json
import re
import statistics
import sys

QUESTION = re.compile(r"^(who|what|when|where|why|how|which|can|could|does|do|is|are|should|will|vs\b)|\?$|\bvs\.?\b", re.I)
INTENT = [
    ("transactional", r"\b(price|pricing|cost|buy|order|discount|coupon|deal|cheap|trial|demo|quote|book|hire|near me)\b"),
    ("commercial", r"\b(best|top|vs|versus|review|reviews|alternative|alternatives|compare|comparison|tool|tools|software|"
                   r"platform|app|service|services|agency)\b"),
    ("informational", r"\b(how|what|why|when|who|guide|tutorial|examples?|meaning|definition|ideas|tips|learn)\b"),
]
STOP = set("""a an and are as at be by can do does for from how i if in is it of on or the to vs what when where which who
why with your you my best top""".split())
BUCKETS = [(1, 1.5), (1.5, 2.5), (2.5, 3.5), (3.5, 5.5), (5.5, 10.5), (10.5, 20.5), (20.5, 1000)]


def num(x):
    x = (x or "").strip().replace("%", "").replace(",", "") if isinstance(x, str) else x
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


def read(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))
    if not rows:
        return []
    head = [h.strip().lower() for h in rows[0]]

    def col(*names):
        for i, h in enumerate(head):
            if any(n in h for n in names):
                return i
        return None
    iq, ip = col("quer", "keyword", "search term"), col("page", "url", "landing")
    ic, ii, ir, iz = col("click"), col("impression"), col("ctr"), col("position", "rank")
    if ic is None or ii is None:       # unknown language: Search Console's own column order
        iq, ic, ii, ir, iz = 0, 1, 2, 3, 4
    out = []
    for r in rows[1:]:
        if not r or not any(r):
            continue
        g = lambda i: r[i] if i is not None and i < len(r) else ""
        clicks, imps = num(g(ic)), num(g(ii))
        ctr = num(g(ir))
        ctr = ctr / 100 if (isinstance(g(ir), str) and "%" in g(ir)) or ctr > 1 else ctr
        out.append({"query": g(iq).strip() if iq is not None else "", "page": g(ip).strip() if ip is not None else "",
                    "clicks": clicks, "impressions": imps, "ctr": ctr if ctr else (clicks / imps if imps else 0),
                    "position": num(g(iz))})
    return out


def bucket(pos):
    for lo, hi in BUCKETS:
        if lo <= pos < hi:
            return f"{lo:g} to {hi - 0.5:g}" if hi < 1000 else "21 and lower"
    return "unknown"


def terms(q):
    return [w for w in re.findall(r"[a-z0-9][a-z0-9'-]+", q.lower()) if w not in STOP and len(w) > 2]


def stem(w):
    for suf in ("ing", "ers", "er", "es", "s"):
        if w.endswith(suf) and len(w) - len(suf) >= 4:
            return w[: -len(suf)]
    return w


def analyse(rows, before=None, brand=(), floor=20):
    by_q = {}
    for r in rows:
        q = r["query"]
        if not q:
            continue
        cur = by_q.setdefault(q, {"query": q, "clicks": 0, "impressions": 0, "pos_x_imp": 0, "pages": {}})
        cur["clicks"] += r["clicks"]
        cur["impressions"] += r["impressions"]
        cur["pos_x_imp"] += r["position"] * r["impressions"]
        if r["page"]:
            cur["pages"][r["page"]] = cur["pages"].get(r["page"], 0) + r["impressions"]
    qs = []
    for q in by_q.values():
        imp = q["impressions"]
        q["position"] = q["pos_x_imp"] / imp if imp else 0
        q["ctr"] = q["clicks"] / imp if imp else 0
        q["branded"] = any(b and b in q["query"].lower() for b in brand)
        q["intent"] = "navigational" if q["branded"] else next(
            (name for name, pat in INTENT if re.search(pat, q["query"], re.I)), "unclear")
        qs.append(q)
    med = {}
    for b in {bucket(q["position"]) for q in qs}:
        vals = [q["ctr"] for q in qs if bucket(q["position"]) == b and q["impressions"] >= floor]
        if len(vals) >= 5:
            med[b] = statistics.median(vals)
    quick = sorted((q for q in qs if 4 <= q["position"] <= 20 and q["impressions"] >= floor and not q["branded"]),
                   key=lambda q: -q["impressions"])
    low_ctr = sorted((q for q in qs if q["impressions"] >= floor and bucket(q["position"]) in med
                      and q["ctr"] < med[bucket(q["position"])] / 2 and q["position"] <= 10),
                     key=lambda q: -q["impressions"])
    questions = sorted((q for q in qs if QUESTION.search(q["query"]) and not q["branded"]), key=lambda q: -q["impressions"])
    clusters = collections.defaultdict(list)
    df = collections.Counter(stem(t) for q in qs for t in set(terms(q["query"])))
    for q in qs:
        ts = [stem(t) for t in terms(q["query"])]
        head = max(ts, key=lambda t: (df[t], t)) if ts else "(other)"
        clusters[head].append(q)
    topics = sorted(({"topic": k, "queries": len(v), "impressions": sum(x["impressions"] for x in v),
                      "clicks": sum(x["clicks"] for x in v),
                      "top": [x["query"] for x in sorted(v, key=lambda x: -x["impressions"])[:5]]}
                     for k, v in clusters.items() if len(v) >= 2), key=lambda t: -t["impressions"])
    competing = sorted(({"query": q["query"], "pages": sorted(q["pages"].items(), key=lambda x: -x[1])}
                        for q in qs if len([p for p, i in q["pages"].items() if i >= floor / 4]) >= 2),
                       key=lambda c: -sum(i for _, i in c["pages"]))
    declines = []
    if before:
        prev = {r["query"]: r for r in analyse(before, None, brand, floor)["all"]}
        for q in qs:
            p = prev.get(q["query"])
            if p and p["clicks"] - q["clicks"] >= 5:
                declines.append({"query": q["query"], "clicks_before": p["clicks"], "clicks_now": q["clicks"],
                                 "position_before": round(p["position"], 1), "position_now": round(q["position"], 1)})
        lost = [p for k, p in prev.items() if k not in by_q and p["clicks"] >= 5]
        declines += [{"query": p["query"], "clicks_before": p["clicks"], "clicks_now": 0,
                      "position_before": round(p["position"], 1), "position_now": None} for p in lost]
        declines.sort(key=lambda d: d["clicks_now"] - d["clicks_before"])
    tot_c, tot_i = sum(q["clicks"] for q in qs), sum(q["impressions"] for q in qs)
    br = [q for q in qs if q["branded"]]
    return {
        "summary": {"queries": len(qs), "clicks": tot_c, "impressions": tot_i,
                    "branded_clicks": sum(q["clicks"] for q in br), "branded_queries": len(br),
                    "intent": dict(collections.Counter(q["intent"] for q in qs)),
                    "median_ctr_by_position": {k: round(v, 4) for k, v in sorted(med.items())}},
        "quick_wins": quick[:30], "low_ctr": low_ctr[:20], "questions": questions[:40], "topics": topics[:25],
        "competing_pages": competing[:20], "declines": declines[:25], "all": qs,
    }


def pct(x):
    return f"{x * 100:.1f}%"


def render(r, has_pages):
    s = r["summary"]
    L = ["# Keyword research from Search Console", "",
         f"- Queries: {s['queries']:,}; clicks: {s['clicks']:,.0f}; impressions: {s['impressions']:,.0f}",
         f"- Branded: {s['branded_queries']} queries, {s['branded_clicks']:,.0f} clicks" if s["branded_queries"] else
         "- Branded queries: none marked (use --brand)",
         "- Intent, from the words in each query: " + ", ".join(f"{k} {v}" for k, v in sorted(s["intent"].items())),
         "- The site's own median click-through by position: " +
         (", ".join(f"{k}: {pct(v)}" for k, v in s["median_ctr_by_position"].items()) or "too little data"), ""]
    L += ["## Quick wins: positions 4 to 20 with impressions", "",
          "| Query | Impressions | Clicks | Position |", "|---|---|---|---|"]
    L += [f"| {q['query']} | {q['impressions']:,.0f} | {q['clicks']:,.0f} | {q['position']:.1f} |" for q in r["quick_wins"]]
    L += ["", "## Low click-through for the position: under half the site's own median", "",
          "| Query | Impressions | CTR | Position |", "|---|---|---|---|"]
    L += [f"| {q['query']} | {q['impressions']:,.0f} | {pct(q['ctr'])} | {q['position']:.1f} |" for q in r["low_ctr"]] or \
         ["| none found | | | |"]
    L += ["", "## Questions searchers ask", ""] + [f"- {q['query']} ({q['impressions']:,.0f} impressions)"
                                                   for q in r["questions"][:25]]
    L += ["", "## Topics: queries grouped by their most shared word", ""]
    L += [f"- {t['topic']}: {t['queries']} queries, {t['impressions']:,.0f} impressions, {t['clicks']:,.0f} clicks. "
          f"For example: {'; '.join(t['top'][:3])}" for t in r["topics"]]
    if has_pages:
        L += ["", "## Queries where several pages compete", ""]
        L += [f"- {c['query']}: " + "; ".join(f"{p} ({i:,.0f})" for p, i in c["pages"][:4]) for c in r["competing_pages"]] \
            or ["- none"]
    if r["declines"]:
        L += ["", "## Declines against the earlier period", "",
              "| Query | Clicks before | Clicks now | Position before | Position now |", "|---|---|---|---|---|"]
        L += [f"| {d['query']} | {d['clicks_before']:,.0f} | {d['clicks_now']:,.0f} | {d['position_before']} | "
              f"{d['position_now'] if d['position_now'] is not None else 'gone'} |" for d in r["declines"]]
    L += ["", "Search Console rounds and leaves out rare queries for privacy, so totals here can differ from the "
              "report's chart. Intent and topics come from the words in each query and need a person's check."]
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("csv")
    ap.add_argument("--compare")
    ap.add_argument("--brand", default="")
    ap.add_argument("--min-impressions", type=float, default=20)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    rows = read(a.csv)
    before = read(a.compare) if a.compare else None
    brand = [b.strip().lower() for b in a.brand.split(",") if b.strip()]
    r = analyse(rows, before, brand, a.min_impressions)
    if a.json:
        out = {k: v for k, v in r.items() if k != "all"}
        print(json.dumps(out, indent=1, default=lambda o: sorted(o.items()) if isinstance(o, dict) else str(o)))
    else:
        print(render(r, any(x["page"] for x in rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
