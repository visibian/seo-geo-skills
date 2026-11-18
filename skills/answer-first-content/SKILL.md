---
name: answer-first-content
description: Write or rewrite a web page so that people and AI assistants can find a clear, sourced answer in it, with the answer first under each heading, specific facts, first-hand experience, dates and named sources, following Google's guidance for its AI features and the published research on what AI answers cite. Use when someone wants a page, article, product or service page that AI search (ChatGPT, Perplexity, Gemini, Google AI Overviews and AI Mode, Copilot) can quote, asks for GEO or AEO content, or wants a draft reviewed for unsourced claims.
license: MIT
metadata:
  author: Visibian
  version: "1.0.0"
---

# Answer-first content

Write pages that answer a real question clearly enough that a person, or an assistant reading the page, can take the answer and trust where it came from. Write for the reader first: Google's guide to its generative AI features (10 July 2026) says there is no need to write in a special way for AI, to split content into small chunks, or to create pages for every variation of a question, and that doing so to manipulate answers breaks its spam policies.

What the research says, with sources and dates: `references/geo-evidence.md`. For the method in depth, three of Visibian Academy's talks are free to read (https://learning.visibian.com/catalogue).

## Steps

1. Pin down the question. One page, one main question a buyer asks in their own words (see the `buyer-questions` skill). Write it at the top of your notes, with who asks it and what they need to decide.
2. Gather what only this brand can say. First-hand experience, its own data, prices, real examples, named experts, customer results the user can share. Google's guide calls this non-commodity content; a page that restates what others already say gives an assistant no reason to use it. Ask the user for these; never invent them.
3. Write the brief with `assets/page-brief.md`: question, reader, the answer in two sentences, the evidence for it, the sub-questions, what the page will not cover.
4. Draft answer-first.
   - Open with the answer in one or two plain sentences, then the detail.
   - Use headings that say what the section answers, and answer it in the first lines under the heading.
   - State facts as specific, checkable sentences: who, what, how much, where, when.
   - Put numbers, quotations and named sources in the text, with the source and date beside each one.
   - Use a table where readers compare (plans, specs, options), and write the conclusion in words too.
   - Show the date the page was last updated where freshness matters (prices, comparisons, guides).
   - Keep the key facts in the page text, not only in images, tabs that load later or PDFs.
5. Check claims. From this skill's folder, run `python3 scripts/claims_check.py draft.md` (Markdown, HTML or text). Source, date, soften or cut every flagged sentence. Then read the draft once more as a sceptical buyer.
6. Finish: a title and meta description that say what the page answers, one H1, structured data that matches the page (see the `structured-data` skill), and links from related pages on the site.

## When rewriting an existing page

Keep what already works for search: the page's address, its main terms and the questions it already answers. Show the user what you cut and why. Never drop a fact, a quotation or a source to make the page shorter without asking.

## Output

- The brief.
- The page, in Markdown or in the site's format.
- The claims check result and how each flag was resolved.

## Ground rules

- Never invent a statistic, a quotation, a customer, a result or a source. If a claim needs evidence the user does not have, say so and leave it out.
- Every claim about how an AI system behaves carries its source and date, and may have changed since.
- No keyword stuffing, no hidden text, no near-duplicate pages for variations of a question.
- Do not promise that a page will be cited. Say what the evidence suggests, and that assistants choose sources in ways no one outside them controls.
