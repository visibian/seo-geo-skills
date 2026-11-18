#!/usr/bin/env python3
"""Generative engine optimization (GEO) for one page, section by section: what an AI answer could quote from it.

Usage:
    python3 passage_check.py https://example.com/guide
    python3 passage_check.py --file draft.html            a built page or a draft in HTML
    Add --json for machine output.

Search engines and assistants often quote one passage, not a whole page. For each section under a heading it reports:
whether the heading is a question, how long the opening sentence is, figures and whether a source link sits in the
same paragraph, quotations, lists and tables, and links to other sites. Counts only, no score. Standard library only;
page_check.py sits beside it.
"""
import argparse
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import page_check  # noqa: E402

FIGURE = re.compile(r"\b\d[\d,.]*\s?(%|percent|per cent|million|billion|thousand|x\b|times)|\b\d{2,}[\d,.]*\b", re.I)
VAGUE = re.compile(r"\b(many|most|some|several|various|numerous|countless|a lot of|significant(ly)?|studies show|"
                   r"experts say|research shows|it is (widely )?(known|believed))\b", re.I)


def main_html(doc):
    body = re.sub(r"<(script|style|noscript|template|svg|nav|header|footer|aside|form)\b.*?</\1>", " ", doc,
                  flags=re.S | re.I)
    m = re.search(r"<(main|article)\b.*?</\1>", body, re.S | re.I)
    return m.group(0) if m else re.sub(r"<head\b.*?</head>", " ", body, flags=re.S | re.I)


def sections(html_main, host=""):
    parts = re.split(r"(<h[1-3]\b[^>]*>.*?</h[1-3]>)", html_main, flags=re.S | re.I)
    out, heading = [], "(before the first heading)"
    for part in parts:
        if re.match(r"<h[1-3]\b", part, re.I):
            heading = page_check.text_of(part)
            continue
        paras = re.findall(r"<(p|li|td|blockquote)\b[^>]*>(.*?)</\1>", part, re.S | re.I)
        texts = [page_check.text_of(x) for _, x in paras]
        text = " ".join(t for t in texts if t)
        if len(text.split()) < 15:
            continue
        lead = next((page_check.text_of(x) for tag, x in paras if tag.lower() == "p" and page_check.text_of(x)), text)
        first = re.split(r"(?<=[.!?])\s+", lead, maxsplit=1)[0]
        figs = sourced = 0
        for tag, frag in paras:
            n = len(FIGURE.findall(page_check.text_of(frag)))
            figs += n
            ext = [h for h in (page_check.attr(t, "href") or "" for t in re.findall(r"<a\b[^>]*>", frag, re.I))
                   if h.startswith("http") and host not in h]
            sourced += n if ext else 0
        out.append({
            "heading": heading, "question": heading.rstrip().endswith("?"),
            "words": len(text.split()), "first_sentence_words": len(first.split()), "first_sentence": first[:240],
            "figures": figs, "figures_with_source_link": sourced,
            "quotations": len(re.findall(r"<blockquote\b|<q\b", part, re.I)) + len(re.findall(r"[“\"][^”\"]{20,}[”\"]", text)),
            "lists": len(re.findall(r"<(ul|ol)\b", part, re.I)), "tables": len(re.findall(r"<table\b", part, re.I)),
            "links_out": len({h for h in (page_check.attr(t, "href") or "" for t in re.findall(r"<a\b[^>]*>", part, re.I))
                              if h.startswith("http") and host not in h}),
            "vague_phrases": sorted({m.group(0).lower() for m in VAGUE.finditer(text)}),
        })
    return out


def render(target, f, secs):
    L = [f"# GEO check: {target}", "",
         f"- Title: {f['title'] or 'none'}",
         f"- Dates in the markup: {', '.join(f'{k} {v}' for k, v in f['dates'].items()) or 'none'}",
         f"- Structured data: {', '.join(f['jsonld_types']) or 'none'}",
         f"- Sections: {len(secs)}; headed by a question: {sum(s['question'] for s in secs)}; opening sentence over "
         f"30 words: {sum(s['first_sentence_words'] > 30 for s in secs)}",
         f"- Figures: {sum(s['figures'] for s in secs)}, with a source link in the same paragraph: "
         f"{sum(s['figures_with_source_link'] for s in secs)}; quotations: {sum(s['quotations'] for s in secs)}; "
         f"links to other sites: {sum(s['links_out'] for s in secs)}", "",
         "| Section | Words | Opening sentence (words) | Figures (with a source link) | Quotations | Lists, tables | "
         "Vague phrases |", "|---|---|---|---|---|---|---|"]
    for s in secs:
        L.append(f"| {s['heading'][:70]}{'?' if s['question'] and not s['heading'].endswith('?') else ''} | {s['words']} | "
                 f"{s['first_sentence_words']} | {s['figures']} ({s['figures_with_source_link']}) | {s['quotations']} | "
                 f"{s['lists']}, {s['tables']} | {', '.join(s['vague_phrases'][:4])} |")
    L += ["", "Counts from the HTML without running scripts. A figure counts as sourced when a link to another site "
              "sits in the same paragraph or list item; read each one, since a link is not always its source."]
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("url", nargs="?")
    ap.add_argument("--file")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if a.file:
        doc, target, host = pathlib.Path(a.file).read_text(encoding="utf-8", errors="replace"), a.file, ""
    elif a.url:
        url = a.url if "://" in a.url else "https://" + a.url
        g = page_check.get(url)
        if g["status"] != 200:
            print(f"{url} answered {g['status'] or g.get('error')}", file=sys.stderr)
            return 2
        doc, target = g["body"], g["url"]
        host = re.sub(r"^https?://", "", g["url"]).split("/")[0]
    else:
        ap.error("give a URL or --file")
    f = page_check.page_facts(doc)
    secs = sections(main_html(doc), host)
    if a.json:
        print(json.dumps({"target": target, "page": {k: f[k] for k in ("title", "dates", "jsonld_types")},
                          "sections": secs}, indent=1))
    else:
        print(render(target, f, secs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
