# Examples

Real output, not mock-ups.

- `visibian.com/seo-audit-report.md`: the `seo-audit` crawler on visibian.com, 40 pages, 17 November 2026 (`python3 scripts/site_audit.py https://visibian.com --max-pages 40 --out seo-audit/`).
- `visibian.com/client-report.html`: the `seo-report` skill's client report, built from that crawl (`python3 scripts/make_report.py seo-audit/audit.json --client "visibian.com" --out client-report.html`). Download it and open it in a browser.

The one blocker in both is real: the links page at visibian.com/links/ builds its list with scripts, so a crawler that runs none sees 21 words.
