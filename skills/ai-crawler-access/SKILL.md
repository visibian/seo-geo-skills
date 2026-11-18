---
name: ai-crawler-access
description: Check and write the robots.txt rules that decide which AI crawlers can read a website (GPTBot, OAI-SearchBot, ChatGPT-User, ClaudeBot, Claude-SearchBot, PerplexityBot, Google-Extended, Googlebot, Bingbot, Applebot, Meta, Amazon, Mistral and more). Use when someone asks whether ChatGPT, Claude, Gemini, Perplexity or Copilot can read their site, whether to block GPTBot or AI training, why an assistant cannot see their pages, or wants robots.txt lines for AI crawlers.
license: MIT
metadata:
  author: Visibian
  version: "1.0.0"
---

# AI crawler access

Help the user decide, check and write which AI crawlers may read their site. Each AI company runs separate crawlers for separate jobs, and blocking the wrong one can take a site out of an assistant's answers.

## The three kinds of crawler

- Search crawlers fetch pages so an assistant can find and cite them in answers (OAI-SearchBot for ChatGPT search, Claude-SearchBot, PerplexityBot, Googlebot for Google Search with AI Overviews and AI Mode, Bingbot for Bing and Microsoft Copilot).
- User fetchers open a page when a person asks an assistant about it (ChatGPT-User, Claude-User, Perplexity-User, meta-externalfetcher, MistralAI-User). Some do not always follow robots.txt.
- Training crawlers and settings collect pages to train models (GPTBot, ClaudeBot, Google-Extended, Applebot-Extended, meta-externalagent, Amazonbot, MistralAI-Training, CCBot).

Blocking training does not remove a site from search answers. OpenAI, for example, treats GPTBot and OAI-SearchBot as separate settings. The full list, with what each crawler does, what blocking it changes and each company's documentation, is in `references/ai-crawlers.md`. Read it before advising on a specific crawler.

## Steps

1. Get the file. In a codebase, look for `robots.txt` in the public or static folder, or for code that generates it (for example `app/robots.ts` in Next.js, a `robots` setting in a CMS, or a server rule). Otherwise fetch it from the live site.
2. Read it with the script, from this skill's folder:
   - live site: `python3 scripts/aicrawlers.py example.com`
   - a file in the codebase: `python3 scripts/aicrawlers.py --file path/to/robots.txt`
   - pasted text: save it to a file, or pipe it with `--stdin`
   - add `--path /pricing --path /blog/some-post` to test the pages that matter most
   If Python or network access is not available, read the file yourself using the rules in `references/matching-rules.md`, and say that you did it by hand.
3. Explain the result in plain words: which assistants can find and cite the site, which cannot, and which training uses are allowed. Lead with anything that blocks a search crawler or a user fetcher, because that removes the site from answers.
4. Ask what the user wants if they have not said. The usual choices are in `references/policies.md`. Training is a business decision with no single right answer; do not push either way.
5. Write the lines. Give the exact robots.txt text for the chosen policy, keep the user's existing rules for other crawlers and paths, and keep the `Sitemap:` line. In a codebase, edit the file or the code that generates it, then run the script again on the result.
6. Check what robots.txt cannot. Firewalls, CDN bot settings and server rules can turn crawlers away whatever robots.txt says. Ask whether the site uses a CDN or security service with AI crawler or bot settings, and tell the user to check them there.

## Output

- A short verdict: who can read the site for answers, who cannot, and what training use is allowed.
- The table from the script, or your own table with the same columns.
- The proposed robots.txt, ready to paste, and what changes for each crawler.
- What you could not check.

## Ground rules

- Report what you observed or what a named source says. Never invent a score, a ranking or a statistic.
- Every claim about how an AI crawler behaves carries its source and the date it was read, and may have changed since.
- Robots.txt is a request. Crawlers that follow it obey it; it is not access control. Do not call it a security measure.
- No robots.txt change guarantees that an assistant names or cites a site. Say that it decides whether the assistant can read the pages, nothing more.
