#!/usr/bin/env python3
"""On-page SEO for one page and the query it should answer: where the query's words appear, and what the page offers.

Usage:
    python3 onpage_check.py https://example.com/pricing --query "project management software pricing"
    python3 onpage_check.py --file dist/pricing/index.html --query "..."     a built page in a codebase
    Add --json for machine output.

It reports observed facts: whether the query's words are in the title, the main heading, the description, the address
and the opening, how the headings are laid out, how long the opening and the sentences are, links to sources and to
the site, images without alt text, structured data, dates, and signs of an author. No density target and no score.
Standard library only; page_check.py sits beside it.
"""
import argparse
import json
import pathlib
import re
import sys
import urllib.parse

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import page_check  # noqa: E402

STOP = set("""a an and are as at be by can do does for from how i if in is it of on or the to vs what when where which who
why with your you my""".split())


def words(text):
    return [w for w in re.findall(r"[a-z0-9][a-z0-9'-]*", (text or "").lower())]


def stem(w):
    for suf in ("ing", "es", "s"):
        if w.endswith(suf) and len(w) - len(suf) >= 4:
            return w[: -len(suf)]
    return w


def covered(query_terms, text):
    have = {stem(w) for w in words(text)}
    return [t for t in query_terms if stem(t) in have]


def main_text(doc):
    body = re.sub(r"<(script|style|noscript|template|svg|nav|header|footer|aside|form)\b.*?</\1>", " ", doc,
                  flags=re.S | re.I)
    main = re.search(r"<(main|article)\b.*?</\1>", body, re.S | re.I)
    return main.group(0) if main else re.sub(r"<head\b.*?</head>", " ", body, flags=re.S | re.I)


def analyse(doc, url, query):
    f = page_check.page_facts(doc)
    terms = [w for w in words(query) if w not in STOP] or words(query)
    main = main_text(doc)
    paras = [page_check.text_of(p) for p in re.findall(r"<p\b[^>]*>(.*?)</p>", main, re.S | re.I)]
    paras = [p for p in paras if len(p.split()) >= 8]
    opening = " ".join(paras[:2])
    text = page_check.text_of(main)
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", text) if len(s.split()) >= 3]
    lens = [len(s.split()) for s in sentences]
    heads = [(int(m.group(1)), page_check.text_of(m.group(2)))
             for m in re.finditer(r"<h([1-4])\b[^>]*>(.*?)</h\1>", doc, re.S | re.I)]
    host = urllib.parse.urlsplit(url).netloc if url else ""
    links = [page_check.attr(t, "href") or "" for t in re.findall(r"<a\b[^>]*>", main, re.I)]
    abs_links = [urllib.parse.urljoin(url or "", h) for h in links if h and not h.startswith(("#", "mailto:", "tel:"))]
    external = [h for h in abs_links if urllib.parse.urlsplit(h).netloc not in ("", host)]
    internal = [h for h in abs_links if urllib.parse.urlsplit(h).netloc in ("", host)]
    imgs = re.findall(r"<img\b[^>]*>", re.sub(r"<noscript\b.*?</noscript>", " ", main, flags=re.S | re.I), re.I)
    author = bool(re.search(r'rel=["\']author["\']|"author"\s*:|itemprop=["\']author|class=["\'][^"\']*\b(byline|author)\b',
                            doc, re.I))
    numbers = re.findall(r"\b\d[\d,.]*\s?(%|percent|million|billion|thousand)?", text)
    slug = urllib.parse.urlsplit(url).path if url else ""
    return {
        "query": query, "terms": terms,
        "title": f["title"], "title_has": covered(terms, f["title"]),
        "h1": f["h1"], "h1_has": covered(terms, " ".join(f["h1"])),
        "description": f["description"], "description_has": covered(terms, f["description"]),
        "url_has": covered(terms, slug.replace("-", " ").replace("/", " ")),
        "opening_words": len(opening.split()), "opening_has": covered(terms, " ".join(text.split()[:100])),
        "headings": heads, "headings_with_terms": [h for _, h in heads if covered(terms, h)],
        "question_headings": [h for lvl, h in heads if lvl > 1 and h.rstrip().endswith("?")],
        "words": len(text.split()), "term_mentions": {t: sum(1 for w in words(text) if stem(w) == stem(t)) for t in terms},
        "avg_sentence_words": round(sum(lens) / len(lens), 1) if lens else 0,
        "long_sentences": sum(1 for n in lens if n > 30),
        "external_links": len(external), "internal_links": len(internal),
        "images": len(imgs), "images_no_alt": sum(1 for t in imgs if page_check.attr(t, "alt") is None),
        "numbers_in_text": len(numbers),
        "jsonld_types": f["jsonld_types"], "dates": f["dates"], "author_signal": author,
        "canonical": f["canonical"], "robots_meta": f["robots_meta"],
    }


def render(r, target):
    yes = lambda has: f"{len(has)} of {len(r['terms'])} words ({', '.join(has) or 'none'})"
    L = [f"# On-page SEO: {target}", f"Query: \"{r['query']}\"", "",
         "## Where the query's words appear", "",
         f"- Title: {r['title'] or 'none'}: {yes(r['title_has'])}",
         f"- Main heading: {' | '.join(r['h1']) or 'none'}: {yes(r['h1_has'])}",
         f"- Description: {r['description'] or 'none'}: {yes(r['description_has'])}",
         f"- Address: {yes(r['url_has'])}",
         f"- First 100 words: {yes(r['opening_has'])}",
         f"- Headings that use them: {len(r['headings_with_terms'])} of {len(r['headings'])}",
         "- Mentions in the main text: " + ", ".join(f"{k} x{v}" for k, v in r["term_mentions"].items()), "",
         "## The page", "",
         f"- Words in the main text: {r['words']}; first two paragraphs: {r['opening_words']} words",
         f"- Average sentence: {r['avg_sentence_words']} words; sentences over 30 words: {r['long_sentences']}",
         f"- Headings: {len(r['headings'])}; written as questions: {len(r['question_headings'])}",
         f"- Links in the main text: {r['external_links']} to other sites, {r['internal_links']} within the site",
         f"- Figures in the text: {r['numbers_in_text']}",
         f"- Images: {r['images']}, without alt: {r['images_no_alt']}",
         f"- Structured data: {', '.join(r['jsonld_types']) or 'none'}",
         f"- Dates: {', '.join(f'{k} {v}' for k, v in r['dates'].items()) or 'none in the markup'}",
         f"- Author shown: {'yes' if r['author_signal'] else 'no sign of one'}",
         f"- Canonical: {r['canonical'] or 'none'}; indexing rules: {r['robots_meta'] or 'none'}", "",
         "## Outline", ""]
    L += [f"{'  ' * (lvl - 1)}- H{lvl}: {h}" for lvl, h in r["headings"][:60]]
    L += ["", "Observed from the HTML, without running scripts. The main text is the page's <main> or <article> when "
              "it has one."]
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("url", nargs="?")
    ap.add_argument("--file")
    ap.add_argument("--query", required=True)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if a.file:
        doc, url, target = pathlib.Path(a.file).read_text(encoding="utf-8", errors="replace"), "", a.file
    elif a.url:
        url = a.url if "://" in a.url else "https://" + a.url
        g = page_check.get(url)
        if g["status"] != 200:
            print(f"{url} answered {g['status'] or g.get('error')}", file=sys.stderr)
            return 2
        doc, url, target = g["body"], g["url"], g["url"]
    else:
        ap.error("give a URL or --file")
    r = analyse(doc, url, a.query)
    print(json.dumps(r, indent=1) if a.json else render(r, target))
    return 0


if __name__ == "__main__":
    sys.exit(main())
