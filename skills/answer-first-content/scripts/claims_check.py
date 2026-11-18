#!/usr/bin/env python3
"""List the sentences in a draft that state a figure, a superlative or a claim about AI with no source or date nearby.

Usage:
    python3 claims_check.py draft.md            Markdown, HTML or plain text
    python3 claims_check.py page.html --json

A sentence is flagged when it holds a number with a unit or a percentage, a superlative ("best", "leading", "#1",
"fastest"), or a claim about an AI system, and its paragraph has no link, no citation in brackets and no year or date.
It is a reading aid: a flagged sentence may be fine (a price on the brand's own page needs no citation), and an
unflagged one may still be wrong.

Standard library only.
"""
import argparse
import html
import json
import pathlib
import re
import sys

FIGURE = re.compile(r"\b\d[\d,.]*\s?(%|percent|per cent|x\b|times\b|million|billion|thousand|users|customers|hours|"
                    r"days|minutes|seconds|ms\b)", re.I)
SUPERLATIVE = re.compile(r"\b(best|leading|#1|number one|fastest|cheapest|most (?:popular|trusted|advanced|accurate)|"
                         r"world[- ]class|industry[- ]leading|unmatched|guaranteed|revolutionary)\b", re.I)
AI = re.compile(r"\b(ChatGPT|OpenAI|Gemini|Claude|Perplexity|Copilot|Grok|AI Overviews?|AI Mode|LLMs?|"
                r"language models?|AI assistants?|answer engines?|generative AI)\b", re.I)
SOURCE = re.compile(r"\]\(https?://|https?://|<a\s|\[\d+\]|\((?:[A-Z][\w&.' -]+,\s*)?(?:19|20)\d{2}\)|"
                    r"\b(?:19|20)\d{2}\b|\b(?:January|February|March|April|May|June|July|August|September|October|"
                    r"November|December)\b|according to|\bsource:", re.I)


def paragraphs(text, is_html):
    if is_html:
        text = re.sub(r"<(script|style|noscript)[^>]*>.*?</\1>", " ", text, flags=re.S | re.I)
        blocks = re.findall(r"<(p|li|td|h[1-6]|blockquote)[^>]*>(.*?)</\1>", text, re.S | re.I)
        return [(html.unescape(re.sub(r"<(?!a\s)[^>]+>", " ", b)), b) for _, b in blocks]
    return [(p, p) for p in re.split(r"\n\s*\n", text) if p.strip()]


def sentences(p):
    return [s.strip() for s in re.split(r"(?<=[.?;:])\s+(?=[A-Z0-9\"'])", re.sub(r"\s+", " ", p)) if s.strip()]


def check(text, is_html):
    out = []
    for plain, raw in paragraphs(text, is_html):
        sourced = bool(SOURCE.search(raw))
        for s in sentences(plain):
            why = [w for w, pat in (("figure", FIGURE), ("superlative", SUPERLATIVE), ("claim about AI", AI))
                   if pat.search(s)]
            if why and not sourced:
                out.append({"sentence": s[:300], "why": why})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("file")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    text = pathlib.Path(a.file).read_text(encoding="utf-8", errors="replace")
    is_html = a.file.lower().endswith((".html", ".htm")) or text.lstrip().lower().startswith(("<!doctype", "<html"))
    found = check(text, is_html)
    if a.json:
        print(json.dumps(found, indent=2, ensure_ascii=False))
        return 0
    if not found:
        print("No unsourced figures, superlatives or claims about AI found.")
        return 0
    print(f"{len(found)} sentence(s) to source, date or soften:")
    for f in found:
        print(f"- [{', '.join(f['why'])}] {f['sentence']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
