# How a crawler reads robots.txt

Use this only when the script cannot run. It follows RFC 9309, the robots.txt standard (IETF, September 2022), and Google's open-source parser, which RFC 9309's authors wrote.

## Getting the file

- The file lives at `/robots.txt` on each host. `www.example.com` and `example.com` are separate hosts with separate files.
- An answer in the 200s: read the rules.
- An answer in the 400s other than 429 (the file is missing or refused): the crawler may read everything.
- An answer in the 500s, a 429 or no answer at all: the crawler treats the whole site as disallowed until it can read the file again.
- A web page served at that address instead of a text file: read as no rules.
- Crawlers read at least the first 500 KiB.

## Groups

- A group starts with one or more `User-agent:` lines and holds the `Allow:` and `Disallow:` lines under them.
- A crawler follows the group that names its product token (for example `GPTBot`), ignoring case. If several groups name it, their rules combine.
- Only when no group names it does it follow `User-agent: *`. A crawler with its own group ignores the `*` group entirely.
- Apple documents one exception: when no group names Applebot, it follows the group for Googlebot.
- `Crawl-delay` and `Sitemap` lines do not end a group.

## Rules

- A rule matches when the path starts with its value. `*` matches any characters, and `$` at the end means the path must end there.
- The longest matching rule wins. When an `Allow` and a `Disallow` are the same length, `Allow` wins.
- An empty `Disallow:` blocks nothing.
- `/robots.txt` itself is always allowed.

## Example

```
User-agent: *
Disallow: /admin/

User-agent: GPTBot
Disallow: /
```

Every crawler may read everything but `/admin/`, except GPTBot, which may read nothing. OAI-SearchBot has no group of its own, so it follows `*` and can read the public pages, which keeps the site in ChatGPT search.
