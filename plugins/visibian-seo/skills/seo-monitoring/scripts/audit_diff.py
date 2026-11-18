#!/usr/bin/env python3
"""What changed on a site between two crawls by site_audit.py: pages lost or added, status codes, redirects,
indexability, titles, descriptions, canonicals, headings, structured data, word counts, links, AI crawler access,
the sitemap and llms.txt, and the findings that appeared or were fixed.

Usage:
    python3 audit_diff.py baseline/audit.json latest/audit.json
    python3 audit_diff.py baseline/audit.json latest/audit.json --words 25 --json
    python3 audit_diff.py baseline/audit.json latest/audit.json --out changes.md

The two files come from the seo-audit skill's crawler with --out (each folder gets an audit.json). Run the same
command, with the same --max-pages, each time; a page missing from one crawl may only be outside its page limit, and
the report says when a crawl reached its limit. Observed differences only. Standard library only.
"""
import argparse
import json
import pathlib
import sys

BLOCKER, FIX, NOTE = "blocker", "fix", "note"


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def n(count, one, many=None):
    return f"{count} {one if count == 1 else (many or one + 's')}"


def rules(p):
    return " ".join(filter(None, [p.get("robots_meta"), p.get("x_robots_tag")])).lower()


def indexable(p):
    canon = p.get("canonical_abs")
    canon_ok = not canon or canon in (p.get("url"), p.get("final_url"))
    return p.get("status") == 200 and "noindex" not in rules(p) and canon_ok and not p.get("robots_blocked")


def why_not_indexable(p):
    if p.get("robots_blocked"):
        return "robots.txt now blocks it"
    if p.get("status") != 200:
        return f"answers {p.get('status') or 'nothing'}" + (f" ({p['error']})" if p.get("error") else "")
    if "noindex" in rules(p):
        return "has noindex"
    return f"its canonical points to {p.get('canonical_abs')}"


def first(v):
    return v[0] if isinstance(v, list) and v else (v if isinstance(v, str) else None)


def hit_limit(a):
    return bool(a.get("max_pages")) and len(a.get("pages", {})) >= a["max_pages"]


def compare(before, after, words_pct=30, words_min=50):
    pb, pa = before.get("pages", {}), after.get("pages", {})
    changes = []   # (level, category, message, [urls])

    def add(level, cat, msg, urls=None):
        changes.append((level, cat, msg, urls or []))

    # site level
    if before.get("robots", {}).get("state") != after.get("robots", {}).get("state"):
        add(BLOCKER if after.get("robots", {}).get("state") == "unreachable" else NOTE, "robots.txt",
            f"robots.txt went from {before.get('robots', {}).get('detail')} to {after.get('robots', {}).get('detail')}.")
    cb = {c["token"]: c for c in before.get("crawlers", [])}
    for c in after.get("crawlers", []):
        old = cb.get(c["token"])
        if old and old.get("access") != c.get("access"):
            closing = c["access"].startswith("closed") or c["access"] == "limited"
            level = BLOCKER if closing and c.get("kind") in ("search", "user") else FIX if closing else NOTE
            add(level, "AI crawlers", f"{c['token']} ({c.get('product', '')}) went from {old['access']} to "
                f"{c['access']} on the home page.")
    sb, sa = before.get("sitemap", {}).get("count", 0), after.get("sitemap", {}).get("count", 0)
    if sb != sa:
        drop = sb and (sb - sa) / sb >= 0.1
        add(FIX if drop else NOTE, "sitemap", f"The sitemap went from {sb:,} to {sa:,} addresses.")
    if before.get("llms_txt") != after.get("llms_txt"):
        add(FIX if not after.get("llms_txt") else NOTE, "llms.txt",
            "llms.txt is gone." if not after.get("llms_txt") else "llms.txt is new.")

    # pages present in only one crawl
    gone = sorted(set(pb) - set(pa))
    new = sorted(set(pa) - set(pb))
    gone_idx = [u for u in gone if indexable(pb[u])]
    if gone_idx:
        where = " The later crawl reached its page limit, so some may only be outside it." if hit_limit(after) else ""
        add(FIX, "pages", f"{n(len(gone_idx), 'indexable page')} from the earlier crawl did not appear in the later "
            f"one: removed, unlinked or out of the sitemap.{where}", gone_idx)
    if new:
        add(NOTE, "pages", f"{n(len(new), 'page')} appeared.", new)

    # pages in both
    lost, regained, status, redirects, titles, descs, h1s, canon, ld, words, orphaned, deeper = \
        [], [], [], [], [], [], [], [], [], [], [], []
    for u in sorted(set(pb) & set(pa)):
        b, a = pb[u], pa[u]
        if indexable(b) and not indexable(a):
            lost.append((u, why_not_indexable(a)))
        elif not indexable(b) and indexable(a):
            regained.append(u)
        if b.get("status") != a.get("status") and not (indexable(b) and not indexable(a)):
            status.append((u, b.get("status"), a.get("status")))
        if (b.get("final_url") != a.get("final_url")) and a.get("chain"):
            redirects.append((u, a.get("final_url")))
        if a.get("status") != 200 or b.get("status") != 200:
            continue
        if (b.get("title") or "") != (a.get("title") or ""):
            titles.append((u, b.get("title"), a.get("title")))
        if (b.get("description") or "") != (a.get("description") or ""):
            descs.append((u, b.get("description"), a.get("description")))
        if first(b.get("h1")) != first(a.get("h1")):
            h1s.append((u, first(b.get("h1")), first(a.get("h1"))))
        if b.get("canonical_abs") != a.get("canonical_abs") and indexable(a):
            canon.append((u, b.get("canonical_abs"), a.get("canonical_abs")))
        tb, ta = set(b.get("jsonld_types") or []), set(a.get("jsonld_types") or [])
        if tb != ta:
            ld.append((u, sorted(tb - ta), sorted(ta - tb)))
        wb, wa = b.get("words") or 0, a.get("words") or 0
        if abs(wa - wb) >= words_min and wb and abs(wa - wb) / wb * 100 >= words_pct:
            words.append((u, wb, wa))
        if (b.get("inlinks") or 0) > 0 and (a.get("inlinks") or 0) == 0 and u != after.get("start"):
            orphaned.append(u)
        if b.get("depth") is not None and a.get("depth") is not None and a["depth"] > b["depth"] + 1:
            deeper.append((u, b["depth"], a["depth"]))

    if lost:
        add(BLOCKER, "indexability", f"{n(len(lost), 'page')} could be indexed before and cannot now: "
            + "; ".join(f"{u} {why}" for u, why in lost[:10]) + ("." if len(lost) <= 10 else ", and more."),
            [u for u, _ in lost])
    if regained:
        add(NOTE, "indexability", f"{n(len(regained), 'page')} can be indexed again.", regained)
    if status:
        add(FIX if any(s and s >= 400 for _, _, s in status) else NOTE, "status codes",
            f"{n(len(status), 'page')} changed status: " + "; ".join(f"{u} {x} to {y}" for u, x, y in status[:10]),
            [u for u, _, _ in status])
    if redirects:
        add(NOTE, "redirects", f"{n(len(redirects), 'address', 'addresses')} now redirect somewhere new: "
            + "; ".join(f"{u} to {d}" for u, d in redirects[:10]), [u for u, _ in redirects])
    if canon:
        add(FIX, "canonicals", f"{n(len(canon), 'canonical')} changed: "
            + "; ".join(f"{u} from {x} to {y}" for u, x, y in canon[:10]), [u for u, _, _ in canon])
    if titles:
        add(NOTE, "titles", f"{n(len(titles), 'title')} changed.", [u for u, _, _ in titles])
    if descs:
        add(NOTE, "descriptions", f"{n(len(descs), 'meta description')} changed.", [u for u, _, _ in descs])
    if h1s:
        add(NOTE, "headings", f"{n(len(h1s), 'main heading')} (h1) changed.", [u for u, _, _ in h1s])
    if ld:
        removed = [u for u, r, _ in ld if r]
        add(FIX if removed else NOTE, "structured data",
            f"Structured data types changed on {n(len(ld), 'page')}"
            + (f"; {len(removed)} lost a type: " + "; ".join(f"{u} lost {', '.join(r)}" for u, r, _ in ld if r)[:900]
               if removed else "") + ".", [u for u, _, _ in ld])
    if words:
        shrunk = [w for w in words if w[2] < w[1]]
        add(FIX if shrunk else NOTE, "content", f"{n(len(words), 'page')} changed length by {words_pct}% or more: "
            + "; ".join(f"{u} {x:,} to {y:,} words" for u, x, y in words[:10]), [u for u, _, _ in words])
    if orphaned:
        add(FIX, "internal links", f"{n(len(orphaned), 'page')} lost every internal link the crawler followed.",
            orphaned)
    if deeper:
        add(NOTE, "internal links", f"{n(len(deeper), 'page')} moved more than one click deeper: "
            + "; ".join(f"{u} {x} to {y}" for u, x, y in deeper[:10]), [u for u, _, _ in deeper])

    # findings that appeared or were fixed (by their wording, which site_audit.py keeps stable)
    key = lambda f: (f["level"], f["category"], f["message"])
    fb = {key(f): f for f in before.get("findings", [])}
    fa = {key(f): f for f in after.get("findings", [])}
    appeared = [fa[k] for k in fa if k not in fb]
    fixed = [fb[k] for k in fb if k not in fa]
    order = {BLOCKER: 0, FIX: 1, NOTE: 2}
    changes.sort(key=lambda c: order[c[0]])
    detail = {"titles": titles, "descriptions": descs, "headings": h1s}
    return {"site": after.get("site"), "before": before.get("checked"), "after": after.get("checked"),
            "pages_before": len(pb), "pages_after": len(pa), "limit_reached": hit_limit(after),
            "changes": [{"level": l, "category": c, "message": m, "urls": u} for l, c, m, u in changes],
            "findings_appeared": appeared, "findings_fixed": fixed,
            "detail": {k: [{"url": u, "before": x, "after": y} for u, x, y in v] for k, v in detail.items()}}


def render(r):
    label = {BLOCKER: "Blockers", FIX: "Fixes", NOTE: "Notes"}
    lines = [f"# What changed on {r['site']}: {r['before']} to {r['after']}", "",
             f"Pages checked: {r['pages_before']} then {r['pages_after']}."
             + (" The later crawl reached its page limit." if r["limit_reached"] else ""), ""]
    if not r["changes"] and not r["findings_appeared"] and not r["findings_fixed"]:
        lines.append("Nothing changed in what the crawler checks.")
        return "\n".join(lines)
    counts = {k: sum(1 for c in r["changes"] if c["level"] == k) for k in label}
    lines += [f"Blockers: {counts[BLOCKER]}. Fixes: {counts[FIX]}. Notes: {counts[NOTE]}.", ""]
    for lvl, title in ((BLOCKER, "Blockers"), (FIX, "Fixes"), (NOTE, "Notes")):
        items = [c for c in r["changes"] if c["level"] == lvl]
        if not items:
            continue
        lines += [f"## {title}", ""]
        for c in items:
            listed = c["message"].count("http") >= min(len(c["urls"]), 10)   # the message already names them
            shown = "" if listed else ", ".join(c["urls"][:10]) + (
                f", and {len(c['urls']) - 10} more" if len(c["urls"]) > 10 else "")
            lines += [f"- {c['category']}: {c['message'].rstrip('.')}.", f"  {shown}" if shown else ""]
        lines.append("")
    for k, title in (("titles", "Titles"), ("descriptions", "Meta descriptions"), ("headings", "Main headings")):
        rows = r["detail"][k]
        if rows:
            lines += ["", f"## {title}, before and after", "", "| Page | Before | After |", "|---|---|---|"]
            esc = lambda s: (s or "(none)").replace("|", "\\|")
            lines += [f"| {x['url']} | {esc(x['before'])} | {esc(x['after'])} |" for x in rows[:30]]
    if r["findings_appeared"] or r["findings_fixed"]:
        lines += ["", "## The audit's findings", ""]
        lines += [f"- New, {f['level']}: {f['message']}" for f in r["findings_appeared"]]
        lines += [f"- Gone, {f['level']}: {f['message']}" for f in r["findings_fixed"]]
    return "\n".join(x for x in lines if x is not None)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("before")
    ap.add_argument("after")
    ap.add_argument("--words", type=int, default=30, help="report length changes of this percentage or more")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out", help="also write the report to this file")
    a = ap.parse_args(argv)
    r = compare(load(a.before), load(a.after), words_pct=a.words)
    text = json.dumps(r, indent=1) if a.json else render(r)
    if a.out:
        pathlib.Path(a.out).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
