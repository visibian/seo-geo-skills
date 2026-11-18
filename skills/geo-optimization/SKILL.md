---
name: geo-optimization
description: Generative engine optimization (GEO) and answer engine optimization (AEO) for an existing page, section by section, so ChatGPT, Perplexity, Claude, Gemini, Copilot and Google AI Overviews and AI Mode can find, understand and quote it, checking question-shaped headings, answer-first openings, self-contained passages, figures with their sources, quotations, lists and tables, dates and vague claims, then rewriting the passages that fall short. Use when someone asks for GEO, AEO or LLM optimization of a page, how to get a page cited or quoted by AI, AI citability, or why assistants quote a competitor's page instead.
license: MIT
metadata:
  author: Visibian
  version: "1.0.0"
---

# GEO: make a page quotable

An assistant that answers from the web reads pages, takes passages and names some of its sources. This skill makes each section of a page a passage worth taking: clear, specific, sourced and current.

What the research says, with sources and dates: `references/geo-evidence.md`. In short: in a lab benchmark, adding statistics, quotations and cited sources raised a page's visibility in generated answers by about 30 to 40%, while keyword stuffing did not (Aggarwal et al., KDD 2024); and Google says its foundational SEO advice applies to its AI features and asks for no special rewriting (Google, 10 July 2026).

## Steps

1. Make sure the page can be read at all: `ai-search-audit` on it (crawler access, text before scripts, snippet rules). A page that cannot be read cannot be quoted.
2. Read it section by section, from this skill's folder:
   `python3 scripts/passage_check.py https://example.com/guide` (or `--file draft.html`).
   For each section: is the heading a question, how long is the opening sentence, how many figures and how many have a source link beside them, quotations, lists and tables, and vague phrases such as "many" or "studies show".
3. Rewrite the weak sections, keeping the author's voice:
   - Open each section with its answer in one or two sentences that make sense alone.
   - Replace vague claims with specific ones: a number, a name, a date, a source. Where the user has no source, mark it for them; do not invent one.
   - Add the brand's own evidence: first-hand data, prices, results, a named expert's quotation with their role.
   - Put comparisons in tables and steps in numbered lists, and say the conclusion in words too.
   - Show when the page was last updated, and update what is out of date.
4. Check the page has what the assistant needs to name the brand: the brand's name with the facts in the text, consistent with its other pages (`brand-fact-sheet`), and structured data that matches (`structured-data`).
5. Run the check again on the rewrite and compare.

## Output

- The table from the script, with the three to five sections to rewrite first.
- Each rewrite: the current passage and the proposed one, side by side.
- Facts the user must supply or confirm.

## Next step

Whether assistants then quote the page or name the brand shows only across many answers over time; a single check proves little. Visibian Brand Intelligence asks the buyers' questions across 11 assistants on a schedule and shows which sources each answer cites (https://visibian.com/brand-intelligence.html); on the plans with API access, its plugin, `visibian-brand-intelligence`, reads the results here. For the method in depth, three of Visibian Academy's talks are free to read (https://learning.visibian.com/catalogue).

## Ground rules

- Counts only, never a citability score: the numbers describe the page, they do not predict an answer.
- Do not split content into fragments or write a page per query variation for AI; Google calls the second scaled content abuse.
- Every claim about how an assistant behaves carries its source and date, and may have changed since.
- No promise that a rewrite gets the page cited.
