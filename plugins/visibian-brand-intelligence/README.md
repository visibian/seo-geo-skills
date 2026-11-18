# Visibian Brand Intelligence

Your Visibian Brand Intelligence data in your AI assistant, through a read-only connector: visibility and share of voice against competitors, wrong facts in AI answers, the sources answers cite, answers that changed, and AI traffic, as briefs, fix plans and client reports. Requires a Visibian workspace with API access.

It works with the Visibian connector: a read-only MCP server that answers from the same data as your Visibian dashboard. API and MCP access come with the Studio, Growth and Network plans; the workspace owner creates a token in Settings, API & MCP access.

## Skills

| Skill | What it does |
|---|---|
| `connect-visibian` | Connects your client to Visibian and fixes connection errors. |
| `visibility-brief` | Writes a weekly or monthly brief against competitors. |
| `competitor-movement` | Shows where competitors gained on you, by assistant, country and topic. |
| `hallucination-fixes` | Traces wrong facts in AI answers to their source and plans the correction. |
| `source-gap-plan` | Finds the pages answers cite where competitors appear and you do not. |
| `answer-drift-review` | Lists answers that changed, and what changed alongside them. |
| `ai-traffic-readout` | Reads visits and crawler fetches from AI services. |
| `client-report` | Drafts monthly AI visibility reports for agency clients. |

## Use it

Install the plugin, give it your token when asked, then ask in plain words, for example:

- "What changed in our AI visibility this month?"
- "Which competitors gained on us in ChatGPT?"
- "What do AI answers get wrong about us, and where does it come from?"

Claude Code asks for the token when the plugin is enabled (or later: `/plugin configure visibian-brand-intelligence@visibian`). In other clients, the `connect-visibian` skill walks you through the setup for Codex, Cursor, VS Code and GitHub Copilot, and Gemini CLI. The connector accepts a token, not an OAuth sign-in, so clients whose custom connectors need OAuth (claude.ai, Cowork, ChatGPT) cannot use it yet.

## Install

| Where | How |
|---|---|
| Claude Code | `/plugin marketplace add visibian/seo-geo-skills`, then `/plugin install visibian-brand-intelligence@visibian` |
| claude.ai and Cowork | Customize, Plugins, Add marketplace, with the address https://github.com/visibian/seo-geo-skills, then install Visibian Brand Intelligence |
| ChatGPT and Codex | `codex plugin marketplace add visibian/seo-geo-skills`, then install Visibian Brand Intelligence from the Plugins Directory in the ChatGPT desktop app or Codex |
| GitHub Copilot CLI | `copilot plugin marketplace add visibian/seo-geo-skills`, then `copilot plugin install visibian-brand-intelligence@visibian` |
| Cursor, VS Code, Gemini CLI and others | see the README at https://github.com/visibian/seo-geo-skills |

## What it runs, sends and stores

- The skills are instructions. They call the Visibian connector, a read-only MCP server at `https://mcp.visibian.com/`, with your token, to read your own workspace's data. The connector cannot change anything in your account.
- Your token is sent only to `mcp.visibian.com`. In Claude Code it is kept in your system's secure storage.
- Requests to the connector are handled under Visibian's privacy policy (https://visibian.com/privacy.html). The plugin itself stores nothing.

## Support

Write to support@visibian.com, or see https://visibian.com/contact.html.

## Licence

MIT. See LICENSE.
