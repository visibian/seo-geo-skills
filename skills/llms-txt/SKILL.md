---
name: llms-txt
description: Write, review or fix an llms.txt file, the markdown file at a site's root that points AI agents and coding assistants to its key pages, following the llmstxt.org format. Use when someone asks for an llms.txt, llms-full.txt, an AI guide file for their site or docs, or whether llms.txt helps them appear in ChatGPT, Gemini or Google's AI answers.
license: MIT
metadata:
  author: Visibian
  version: "1.0.0"
---

# llms.txt

Write or check an llms.txt file, and tell the user plainly what it does and does not do.

## What to tell the user first

- llms.txt is a proposal (llmstxt.org, Jeremy Howard, first published 3 September 2024, now in its second version). It is a short markdown file that guides agents to a site's key pages.
- It is used most by coding agents reading software documentation. The AI labs publish llms.txt files for their own developer docs, and Chrome's Lighthouse checks for one in its agentic browsing audit (llmstxt.org, v2).
- Google Search does not use it. Google's guide to generative AI features (updated 10 July 2026) lists llms.txt among the things to ignore for Google Search, and says it "will neither harm nor help" a site there.
- No major AI assistant has documented that it reads llms.txt to answer questions about a brand. Say so, and present the file as a low-cost aid for agents and documentation, not a visibility lever.

Sources and dates: `references/sources.md`.

## Steps

1. Check for an existing file. From this skill's folder: `python3 scripts/check_llms_txt.py example.com` (or `--file path/to/llms.txt` in a codebase). Add `--links` to find links that no longer open.
2. Gather the key pages. Read the sitemap, the main navigation and the footer, or the codebase's routes. Pick the pages an agent would need to answer questions about the business: what it is, products and prices, docs, policies, contact. Keep the list short.
3. Write the file in the order the format requires:
   - `# Site name` (the only required part);
   - `> one-sentence summary` of what the business does and for whom;
   - optional plain paragraphs for key facts or how to read the site (no headings);
   - `## Section` headings, each with a list of `- [Page name](https://full-url): what the page covers`;
   - an optional `## Optional` section for secondary links.
   Use full URLs. Write each note as a plain fact from the page, not marketing copy. A template is in `assets/llms-template.txt`.
4. Place it at the site root (`/llms.txt`), or under a path it should cover (`/docs/llms.txt`). In a codebase, put it in the public or static folder, or add a route that serves it as plain text.
5. Optional: markdown copies. The format suggests serving a clean markdown copy of key pages at the same URL with `.md` added, and pointing to it with `<link rel="alternate" type="text/markdown">`. Suggest this for documentation sites only, where agents use it most.
6. Check the result with the script again.

## Output

- The llms.txt, ready to save, or the fixes to the existing one.
- The checker's result.
- One line on what the file will and will not do.

## Ground rules

- Every link must open and every note must match its page. Never list a page that does not exist.
- Do not claim llms.txt improves rankings or AI visibility. Report what the sources say, with their dates.
