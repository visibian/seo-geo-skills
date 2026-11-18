# Changelog

## 1.0.1 (18 November 2026)

- The tests run on Python 3.9, 3.12 and 3.14. GitHub's newest Ubuntu runner has no Python 3.9, so the 3.9 tests run on Ubuntu 24.04, and one version's failure no longer cancels the others.
- The scripts close each error response from a server as soon as they have read it, and the tests close their local servers, so a run leaves no open connections behind.

## 1.0.0 (17 November 2026)

- First release: the Visibian SEO & GEO plugin (24 free skills for search engine optimization and AI search) and the Visibian Brand Intelligence plugin (eight skills on the read-only Visibian connector), packaged for Claude, ChatGPT and Codex, GitHub Copilot and VS Code, Cursor, Kiro, Gemini CLI and other clients that read Agent Skills.
