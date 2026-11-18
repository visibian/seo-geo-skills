# Connecting each client

The server: `https://mcp.visibian.com/`, Streamable HTTP, header `Authorization: Bearer <token>`. Checked against each client's documentation on 5 November 2026. Keep the token in an environment variable named `VISIBIAN_API_TOKEN` or in the client's secure prompt, never in a file that is committed.

## Claude Code

With this plugin installed, Claude Code asks for the token when the plugin is enabled from `/plugin` and keeps it in the system's secure storage. Installed from the command line (`claude plugin install`), it is installed without the token: set it with `/plugin configure visibian-brand-intelligence@visibian` (tested 17 November 2026). To connect without the plugin:

```bash
claude mcp add --transport http visibian https://mcp.visibian.com/ --header "Authorization: Bearer $VISIBIAN_API_TOKEN"
```

This stores the token in Claude Code's local configuration for the user, not in the project. Do not add it with `--scope project`, which writes `.mcp.json` into the repository. Check with `/mcp`.

## Claude (claude.ai, Claude Desktop, Cowork)

Custom connectors there sign in with OAuth, or, for some organizations, an Owner can add a request header when adding the connector (a beta). The Visibian connector does not offer OAuth sign-in yet. Until it does, use Claude Code, or ask the organization's Owner whether **Request headers** appears when adding a custom connector.

## Codex CLI

Add to `~/.codex/config.toml`:

```toml
[mcp_servers.visibian]
url = "https://mcp.visibian.com/"
bearer_token_env_var = "VISIBIAN_API_TOKEN"
```

Then set `VISIBIAN_API_TOKEN` in the shell that starts Codex, and check with `codex mcp list`.

## ChatGPT

Plugins in ChatGPT's public Plugins Directory connect through OAuth or with no authentication; OpenAI's submission guide (read 5 November 2026) says its connection form has no bearer-token input. Whether the **Add custom MCP server** form in ChatGPT accepts a bearer token was not confirmed on that date: try it under Plugins, and if it offers only OAuth or no authentication, the Visibian connector cannot connect there until it offers OAuth sign-in. Codex CLI works today (above).

## Cursor

In `~/.cursor/mcp.json` (all projects) or `.cursor/mcp.json` (one project, and then keep the token out of it):

```json
{
  "mcpServers": {
    "visibian": {
      "url": "https://mcp.visibian.com/",
      "headers": { "Authorization": "Bearer ${env:VISIBIAN_API_TOKEN}" }
    }
  }
}
```

Cursor reads `${env:NAME}` from the environment. Set `VISIBIAN_API_TOKEN` in the shell profile.

## VS Code and GitHub Copilot

In `.vscode/mcp.json`, with a prompt so the token is never written to the file:

```json
{
  "inputs": [
    { "type": "promptString", "id": "visibian-token", "description": "Visibian API token", "password": true }
  ],
  "servers": {
    "visibian": {
      "type": "http",
      "url": "https://mcp.visibian.com/",
      "headers": { "Authorization": "Bearer ${input:visibian-token}" }
    }
  }
}
```

## Gemini CLI

```bash
gemini mcp add -s user -t http visibian https://mcp.visibian.com/ -H "Authorization: Bearer $VISIBIAN_API_TOKEN"
```

`-s user` keeps it in the user's settings rather than the project's. The shell expands the variable, so the token is stored in `~/.gemini/settings.json`; keep that file private.

## Any other MCP client

Any client that can send an `Authorization` header to a Streamable HTTP MCP server can connect with the same three values: the URL, the transport and the header. Check the client's documentation for where headers go and how it stores secrets.

## The REST API

The same 13 operations are available without an assistant at `https://app.visibian.com/api/v1`, with the same token, read-only, 120 requests a minute (https://docs.visibian.com/developers.html).
