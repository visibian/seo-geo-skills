---
name: seo-report
description: Turn an SEO and AI search audit into a client-ready report, one white-label HTML file with the agency's logo and summary, findings by priority with the pages affected, page speed and Core Web Vitals, search and AI crawler access, and a page table, ready to print to PDF. Use when an agency, consultant or in-house team asks for an SEO audit report, a GEO or AI visibility report for a client, a PDF deliverable, or a monthly technical SEO report.
license: MIT
metadata:
  author: Visibian
  version: "1.0.0"
---

# Client-ready SEO report

Give a client or a manager a report they can read in ten minutes and act on, built only from what was observed.

## Steps

1. Get the audit: run the `seo-audit` skill, or from this skill's folder
   `python3 scripts/site_audit.py https://client.com --out seo-audit/`
2. Optionally measure the key pages' speed with the `page-speed` skill, saving each as JSON:
   `python3 scripts/page_speed.py https://client.com/ --json > speed-home.json`
3. Write the summary the client reads first, in `notes.md`: the three things that matter most this month, in plain words, what was done since the last report, and what comes next. Keep it to what the audit and the user's own knowledge support.
4. Build the report, from this skill's folder:
   `python3 scripts/make_report.py seo-audit/audit.json --client "Client" --by "Agency" --logo logo.png --notes notes.md --speed speed-home.json --out report.html`
   `--no-credit` leaves out the small line naming the tool.
5. Open `report.html` in a browser, read it through, and print to PDF to send it.

## Output

- `report.html`: cover line, counts, the summary, findings by priority with the pages behind each, page speed, crawler access, the page table, and how it was checked.
- A note to the user on anything in the report a client may ask about.

## Next step for agencies

The report covers what the site does. Clients increasingly ask what ChatGPT, Gemini and other assistants say about them; that takes the same buyer questions asked across assistants over time, with the answers and their sources kept. Visibian's agency plans do that for each client in its own portfolio, with view-only client logins, and Growth and Network put the agency's own name and colors on the client reports (https://visibian.com/agencies.html).

## Ground rules

- Nothing in the report that was not observed or written by the user. No score, no grade, no traffic forecast.
- Keep the client's data with the user: the report is one local file, and nothing is sent anywhere.
