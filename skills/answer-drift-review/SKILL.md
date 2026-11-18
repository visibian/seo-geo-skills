---
name: answer-drift-review
description: Review which AI answers about the brand changed, from the user's Visibian Answer Drift data, covering the questions whose answer changed materially, on which assistant and when, and whether the brand was gained or lost, then line the changes up with the sources and facts behind them. Use when someone asks why an assistant stopped or started mentioning them, what changed in ChatGPT, Gemini or Perplexity answers recently, or for an answer drift report, and the Visibian connector is available.
license: MIT
metadata:
  author: Visibian
  version: "1.0.0"
---

# Answer drift review

Answers change all the time; most changes do not matter. This skill finds the ones that do, lost or gained mentions on questions that matter, and what else changed at the same time. How to read the data: `references/reading-visibian-data.md`.

## Steps

1. Portfolio and window. `list_portfolios`, then `get_answer_drift` for 30 days (or the window the user asks about).
2. Keep the material changes. Filter to material changes, then to those where the brand was gained or lost. Group by question and by model.
3. Put them on a timeline: for each lost or gained mention, the date, the model, the question and the drift score.
4. Look for what moved with them, without claiming cause:
   - `get_visibility_series` around the same dates: one question or a wider shift?
   - `list_source_pages` for the window: did the pages the answers use change, for example a competitor's new comparison page or a review site's update?
   - `list_hallucinations`: did a wrong fact appear at the same time?
   - Anything the user changed on their own site in that period (ask).
5. Write it up in the format below and suggest one check for each important loss.

## Format

```
## Answers that changed: [portfolio], [from] to [to]

Material changes: [n]. Brand lost in [n] answers, gained in [n].

| Date | Model | Question | Brand | Drift score |
|---|---|---|---|---|

### What moved at the same time

[Facts from the other tools, each with its date.]

### Worth checking

[For each important loss, one thing to check, phrased as a question.]
```

## Ground rules

- Only changes the tool returned, with their dates and models. Never infer a change that is not in the data.
- Same timing is not cause. Say "at the same time as", never "because of", unless the user has evidence.
- One lost answer on one model is worth watching, not acting on alone.
