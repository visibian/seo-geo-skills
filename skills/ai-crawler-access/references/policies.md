# Common robots.txt policies for AI crawlers

Each of these policies is a starting point. Merge it with the user's existing rules: keep their groups for other crawlers, their private paths and their `Sitemap:` line. Facts about each crawler are in `ai-crawlers.md`, from each company's own documentation, read on the date given there.

## A. Open to AI answers and to training

Nothing to add for AI crawlers. A file with no group for them, or this, lets every crawler read the public pages:

```
User-agent: *
Disallow:

Sitemap: https://example.com/sitemap.xml
```

Check that no other group names an AI crawler with `Disallow: /`.

## B. Open to AI answers, closed to training

Keeps the search crawlers and user fetchers, closes the crawlers and settings used for training:

```
User-agent: GPTBot
User-agent: ClaudeBot
User-agent: Applebot-Extended
User-agent: meta-externalagent
User-agent: MistralAI-Training
User-agent: CCBot
Disallow: /

User-agent: *
Disallow:
```

Two trade-offs to tell the user before they add more names:

- Google-Extended stops Google using the pages to train Gemini **and** to feed facts into answers in the Gemini app. It does not change Google Search, AI Overviews or AI Mode. A brand that wants to be named in the Gemini app should think twice before adding it.
- Amazonbot collects pages for Amazon's products and services, including Alexa, and may be used for training. Closing it also closes Alexa's use of the pages.

## C. Out of one assistant's answers

Name only that assistant's search crawler and user fetcher, for example ChatGPT:

```
User-agent: OAI-SearchBot
User-agent: ChatGPT-User
Disallow: /
```

OpenAI says a change to OAI-SearchBot takes about 24 hours. ChatGPT-User does not always follow robots.txt, so it may still open a page a user asks for.

## D. Out of Google's AI answers but still in Google Search

Robots.txt cannot do this: AI Overviews and AI Mode follow Googlebot, and blocking Googlebot removes the site from Google Search too. The options Google gives:

- the **Search generative AI** setting in Search Console (added in 2026), which takes the site out of AI Overviews, AI Mode and the AI features in Discover;
- `nosnippet`, `data-nosnippet`, `max-snippet` or `noindex` on the pages concerned.

## E. A private area closed to every crawler

```
User-agent: *
Disallow: /account/
Disallow: /checkout/
```

A crawler with its own group ignores the `*` group. If the file also has a group for, say, GPTBot, repeat the private paths there.

## What robots.txt cannot do

- It does not stop a crawler that ignores it, and some user fetchers do not always follow it.
- It does not override a firewall or CDN rule. Several CDN and security services can turn AI crawlers away on their own settings; check them.
- It does not hide pages that are already public elsewhere, and it does not remove pages already used for training.
