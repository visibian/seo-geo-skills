---
name: connect-visibian
description: Connect an AI assistant or coding agent to the user's Visibian account through the Visibian connector (an MCP server at mcp.visibian.com that reads their AI visibility data), check that it works, and fix connection errors such as 401, 403 or 429. Use when someone wants to set up Visibian in Claude, Claude Code, ChatGPT, Codex, Cursor, VS Code, GitHub Copilot or Gemini CLI, asks where to find their Visibian API token, or when a Visibian tool call fails.
license: MIT
metadata:
  author: Visibian
  version: "1.0.0"
---

# Connect Visibian

Set up the Visibian connector so the other skills in this plugin can read the user's data, then check it.

## What the user needs

- A Visibian workspace on a plan with API access: **Studio, Growth or Network**.
- A token: the workspace owner creates it in the Visibian dashboard, **Settings, API & MCP access**. It starts with `vsb_` and is shown once. A token stops working when it is revoked or when the plan ends, and works again when the plan is back.
- The server: `https://mcp.visibian.com/`, Streamable HTTP, sending the token as `Authorization: Bearer <token>`. It is read-only and sees one workspace.

Never ask the user to paste the token into the conversation. Tell them where to put it, and use an environment variable or the client's secure prompt.

## Steps

1. Check whether it already works: call `list_portfolios`. If it returns the workspace name and portfolios, the connection is ready; say which workspace it is.
2. If no Visibian tools are available, find the client the user is in and follow its section in `references/clients.md`. Today the connector accepts a bearer token and does not offer an OAuth sign-in, so clients whose custom connectors require OAuth cannot connect to it yet; the reference says which.
3. If a call fails, read the error with the table in `references/reading-visibian-data.md` and tell the user the fix in one or two sentences.
4. Once it works, list the portfolios and suggest a first question, for example "What changed in our visibility over the last 30 days?" (the `visibility-brief` skill).

## Ground rules

- Never print, log or repeat a token. Never store one in a file that is committed to a repository.
- Do not claim a client supports the connector unless its section in `references/clients.md` says so; when in doubt, say what to try and that it is unconfirmed.
