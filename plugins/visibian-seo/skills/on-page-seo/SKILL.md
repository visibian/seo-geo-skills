---
name: on-page-seo
description: Optimize one page for the query it should rank and be cited for, in Google and in AI answers (ChatGPT, Perplexity, Gemini, Google AI Overviews and AI Mode), checking the title tag, meta description, H1 and headings, URL, opening paragraph, E-E-A-T signals (author, dates, sources), internal links, images and structured data, then rewriting what falls short. Use when someone asks to optimize a page, improve on-page SEO, rewrite a title or meta description, target a keyword, or why a specific page does not rank or get cited.
license: MIT
metadata:
  author: Visibian
  version: "1.0.0"
---

# On-page SEO

Make one page the clearest answer to one query, for a reader, for Google, and for an assistant that may quote it.

## Before you start

- Get the page and the query it should answer. If the user does not know the query, use `keyword-research` (Search Console) or `buyer-questions` first. One page, one main need.
- Check that no other page on the site targets the same query; if one does, decide which page answers before editing.

## Steps

1. Read the page, from this skill's folder:
   `python3 scripts/onpage_check.py https://example.com/page --query "the query"` (or `--file` for a built page).
   It shows where the query's words appear, the outline, the opening, sentence length, links, figures, images, structured data, dates and signs of an author.
2. Read the page as the searcher would. Does the first paragraph answer the question? Is it clear who wrote it and when? Are claims backed by named sources? Would a reader trust it enough to act?
3. Rewrite, in this order:
   - Title: what the page offers, in the searcher's words, specific enough to choose over the next result. Google shows a title link in place of the title for some pages and cuts long ones to fit the screen (Google Search Central, "Influencing your title links", updated 10 December 2025).
   - Main heading and opening: the answer in the first two or three sentences, then the detail.
   - Headings: the sub-questions the reader has, in the order they have them; some as questions where that is how people ask.
   - Body: facts with their source and date, figures with their unit and source, steps as numbered lists, comparisons as tables. Each section should make sense on its own, since search engines and assistants may quote one passage.
   - Signals of who stands behind it: the author with a short line on their experience, the date updated, a link to the about or contact page (Google Search Central, "Creating helpful, reliable, people-first content", updated 5 October 2026, which asks who made the content, how and why).
   - Description: a summary that makes the click worth it; Google may write its own snippet, and sets no length limit but cuts to fit (Google Search Central, "Control your snippets in search results", updated 20 April 2026).
   - Links: to the pages a reader needs next, with anchors that say what they are; out to the sources cited.
   - Structured data that matches what the page shows (`structured-data`).
4. In a codebase, edit the page's source; then run the script again on the result.

## Output

- The current title, H1 and description beside the proposed ones.
- The rewritten opening, and the outline with the headings to add, change or drop.
- A short list of other changes (sources to add, author and dates, links, images, structured data).

## Ground rules

- No keyword density targets and no score. Use the query's words where they read naturally; Google's spam policies count keyword stuffing as spam (Google Search Central, "Spam policies for Google web search", updated 28 August 2026).
- Never invent facts, figures, reviews or author credentials to fill a gap; mark it for the user instead.
- Do not promise a ranking or a citation.
