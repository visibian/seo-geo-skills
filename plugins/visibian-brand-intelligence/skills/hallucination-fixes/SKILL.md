---
name: hallucination-fixes
description: Turn the misinformation flags in the user's Visibian Hallucination Watch (AI answers that contradict the brand's fact sheet) into a plan to fix each wrong fact at its source, grouped by fact and severity, with the assistant, question and evidence for each. Use when someone asks what AI assistants get wrong about their brand, wants to fix hallucinations, outdated prices or wrong facts in ChatGPT, Gemini or other answers, and the Visibian connector is available.
license: MIT
metadata:
  author: Visibian
  version: "1.0.0"
---

# Hallucination fixes

Assistants repeat what they find. The fix for a wrong answer is almost always a page somewhere that states the wrong fact, or a right fact the brand never stated plainly. This skill turns Visibian's flags into that list of pages to fix. How to read the data: `references/reading-visibian-data.md`.

## Steps

1. Get the flags. `list_portfolios`, then `list_hallucinations` for the portfolio. Start with `severity: critical`.
2. Group them by fact (`fact`): one group per wrong fact, with how many flags, which models, the questions (`prompt`), what the answer said (`model_said`), what the fact sheet says (`expected`), the `verdict`, `confidence` and the `evidence` snippet.
3. Check the fact sheet first. If the flagged answer looks right and the fact sheet looks out of date (an old price, a former executive), say so: the fix is to update the fact sheet in Visibian, not the web.
4. For each real error, find the likely source:
   - Is the right fact stated plainly on the brand's own site, in the page text? If not, that is the first fix.
   - Do the brand's own pages disagree with each other? Use the `brand-fact-sheet` skill's script if it is installed.
   - Does an old page, directory listing, review site, press article or partner page state the wrong version? `top_sources` and `list_source_pages` for the portfolio show which pages the answers use.
5. Write the plan in the format below, most severe and most repeated first.

## Format

```
## Wrong facts in AI answers: [portfolio], as of [date]

| Fact | Answers said | Your fact sheet says | Flags | Models | Severity |
|---|---|---|---|---|---|

### [Fact 1]
- Example: [model], asked "[question]": "[short quote of what it said]"
- Likely source: [page or profile, and what it says] (or: not found; the right fact is not stated plainly on the site)
- Fix: [the change, on which page, and who can make it]
```

## Ground rules

- Use the flags as returned. Do not decide yourself that an answer is right or wrong beyond pointing out where the fact sheet may be out of date.
- Never suggest arguing with an assistant, flooding the web with new pages or posting fake content. Fix the sources.
- Say that a fixed source reaches answers over time and at a pace no one outside the assistants controls.
