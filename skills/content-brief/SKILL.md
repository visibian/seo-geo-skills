---
name: content-brief
description: Write an SEO and GEO content brief for a new page or a rewrite, covering the search intent, the target query and related questions, the outline with answer-first sections, what the pages already ranking or cited for the topic cover, the facts and sources to cite, internal links, structured data and how the page will be measured. Use when someone asks for a content brief, a blog post outline, an article plan, what to write to rank for a keyword or get cited by ChatGPT, Perplexity or Google AI Overviews, or a brief for a writer or an AI writer.
license: MIT
metadata:
  author: Visibian
  version: "1.0.0"
---

# Content brief

Plan a page so that whoever writes it, a person or a model, produces the best answer to one need, with the facts and sources to back it.

## Steps

1. Pin the need. One main query or question, the reader (who they are, what they already know), and what they should be able to do after reading. If the user has Search Console data, start from `keyword-research`; if not, from `buyer-questions`.
2. Look at what already answers it. Ask the user for the pages that rank or that assistants cite for this question (from a search they run, or from their Visibian data if the connector is set up), plus their own closest page. Then, from this skill's folder:
   `python3 scripts/page_outline.py URL1 URL2 URL3`
   It lays the outlines side by side and lists the headings several pages share.
3. Decide the angle: what the page will add that the others lack (first-hand data, a worked example, a clear recommendation for a named situation, an up-to-date comparison). Without one, say so; another page like the rest is rarely worth writing.
4. Gather the facts: each claim the page will make, with its source and date. Mark gaps for the user to fill from their own knowledge; never fill them with invented figures.
5. Fill the brief from `assets/brief-template.md`.

## Output

The brief, from the template: the need and reader, the query and related questions, the angle, the outline with the answer each section opens with, the facts with sources, the pages to link to and from, structured data, and the checks to run on the draft (`on-page-seo`, `answer-first-content`).

## Ground rules

- Briefs describe what to say and why, not how many words or keywords to use. Length follows the need.
- Other sites' pages are for understanding what readers expect, never for copying text or structure wholesale.
- Every fact in the brief carries its source and date, or is marked as the user's to confirm.
