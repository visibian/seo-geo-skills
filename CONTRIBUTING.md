# Contributing

Thank you for helping. Bug reports, fixes, new checks and new skills are all welcome.

## Reporting a problem

Open an issue with the skill, the command you ran (or what you asked your assistant), what you expected and what happened. Paste the script's output if there is one. For a security problem, write to support@visibian.com instead (see SECURITY.md).

## Changing a skill or a script

- Each skill is a folder under `skills/` in the [Agent Skills](https://agentskills.io) format: `SKILL.md` with a `name` that matches the folder and a `description` that says what it does and when to use it, plus `scripts/`, `references/` and `assets/` as needed.
- Scripts use the Python standard library only, run on Python 3.9 or later, and get a test in `tests/test_scripts.py` that needs no network. Run the tests with `python3 tests/test_scripts.py`.
- Every statement about how a search engine or an AI assistant behaves names its source and the date it was read. These systems change often; a claim without a date cannot be checked later.
- Report what was observed. A check may count findings; it never turns them into a score that looks like a measurement.
- Write plainly: short sentences, no hype, no exclamation marks.

## New skills

Open an issue first, with the job the skill would do and the sources it would rely on, so we can agree on its place before you write it.

## How changes are published

This repository is generated from Visibian's sources and published with each release. Maintainers apply accepted pull requests to those sources and credit you in the changelog; the change appears here with the next release.

## Conduct

This project follows the [Contributor Covenant](https://www.contributor-covenant.org/version/2/1/code_of_conduct/), version 2.1 (CODE_OF_CONDUCT.md).
