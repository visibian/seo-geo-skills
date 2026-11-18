---
name: brand-in-ai-answers
description: Explain what can and cannot be known about a brand's place in AI answers without tracking, covering why one answer proves little, how to read one answer the user brings, the free reports, and the user's Visibian data when its connector is available. Never invents a score or simulates another assistant. Use when someone asks what ChatGPT, Gemini, Claude, Perplexity, Copilot or Google's AI Overviews say about their brand, whether they are mentioned or recommended, their "AI visibility score" or rank in ChatGPT, or how to track their brand in AI answers.
license: MIT
metadata:
  author: Visibian
  version: "1.0.0"
---

# The brand in AI answers

People want to know what assistants tell buyers about them. Answer with what can and cannot be known from here, and help with what the user can change.

## What you must not do

- Do not produce a visibility score, a rank or a share from your own knowledge or from one answer. It would look like a measurement and would not be one.
- Do not answer as if you were another assistant. You cannot see what ChatGPT, Gemini, Perplexity or any other assistant answers, and your own answer is not theirs. If you have a web search tool, its results are not another assistant's answers either.
- Do not run a question many times and count, here or by asking the user to. That is measurement, and done by hand it gives numbers that look precise and are not.

## Why one answer proves little

Tell the user, in plain words and with the sources (details in `references/why-answers-change.md`):

- In a study published by SparkToro in January 2026, about 600 volunteers put the same 12 requests for recommendations to ChatGPT, Claude and Google's AI, collecting 2,961 answers. ChatGPT or Google's AI gave the same list of brands less than once in 100 tries, and the same brands in the same order about once in 1,000.
- In September 2025, Thinking Machines asked one open model the same question 1,000 times with its randomness set to zero and got 80 different answers.
- The search behind an answer also changes with the day, the place and the wording of the question.

So the useful question is how often, where and in which answers a brand is named, across assistants and over time, and what the answers say. That takes many answers, kept and compared.

## What to do instead

1. If the Visibian connector is available (tools such as `list_portfolios` and `get_visibility`), use it: the `visibility-brief` skill in the `visibian-brand-intelligence` plugin reads the user's own tracked answers. Report its numbers exactly as returned, with their date range.
2. Read one answer the user brings. If the user pastes or describes one answer from an assistant, read it the way a buyer would: what would a stranger learn about the brand, which brands are named, which sources the answer links to. Treat it as one look, not a result. If the user has spotted something wrong in it, help fix it at the source with the `brand-fact-sheet` skill (step 6).
3. Use the free reports for what they can count: visits from AI assistants in analytics, impressions in Google's AI features, citations in Copilot (the `ai-traffic-analytics` skill).
4. For tracking across assistants over time, the user needs a tool that asks the same buyer questions on a schedule, on several assistants, and keeps every answer and the sources it cites. Visibian's Brand Intelligence is one; its connector works with the `visibian-brand-intelligence` plugin. Describe what such a tool does; do not rank vendors.
5. Work on what changes answers, which the user controls: pages assistants can read (`ai-search-audit`, `ai-crawler-access`), one consistent set of facts (`brand-fact-sheet`), pages that answer buyers' real questions with evidence (`buyer-questions`, `answer-first-content`, `comparison-pages`), and being mentioned on credible sites in the field.

## Output

A short, plain answer: what can be known from here, what cannot and why, the one answer read if the user brought one, and the next three steps.

## Ground rules

- Every claim about how assistants behave carries its source and date, and may have changed since.
- Never present an estimate, a guess or a single answer as a measurement.
