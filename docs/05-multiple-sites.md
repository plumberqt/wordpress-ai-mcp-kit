# 05 — Connect multiple websites

The same kit works for many sites. Two things must be **unique per site**: the endpoint URL and the credentials. Everything else is identical.

---

## One project per site (recommended)

The cleanest approach: each site gets its own project folder with its own `.opencode/opencode.json`.

```
D:\work\
├── site-a\                 ← client A
│   └── .opencode\opencode.json   → secret WP_APP_PASSWORD_A
├── site-b\                 ← client B
│   └── .opencode\opencode.json   → secret WP_APP_PASSWORD_B
└── my-blog\
    └── .opencode\opencode.json   → secret WP_APP_PASSWORD_C
```

Copy [`examples/site-switch-template.jsonc`](../examples/site-switch-template.jsonc) into each, and change the **three** marked values.

**Why per-project is best:** run opencode inside `site-a\` and it only ever sees site A. Impossible to "oops, edited the wrong site".

---

## Step-by-step for a new site

### On the new WordPress site

1. Install **MCP Adapter** + **Enable Abilities for MCP** (see [01](01-install-plugins.md)).
2. Create user **`ai-agent`** (Editor) and an **Application Password** (see [02](02-wordpress-ai-user.md)).
3. Install **`ai-office-hours.zip`** and configure it (see [03](03-ai-office-hours.md)).
4. Note the endpoint: `https://SITE-B.com/wp-json/mcp/mcp-adapter-default-server`

### On your computer

5. Save the new password under a **new variable name** so it doesn't clash:
   ```powershell
   setx WP_APP_PASSWORD_SITE_B "wwww xxxx yyyy zzzz"
   ```
6. In the new project's `.opencode/opencode.json`, set:
   - `WP_API_URL` → site B's endpoint
   - `WP_API_USERNAME` → `ai-agent`
   - `WP_API_PASSWORD` → `{env:WP_APP_PASSWORD_SITE_B}`
7. Restart your editor, then `opencode mcp list` → `wordpress ✓ connected`.

---

## Same variable name across sites? Be careful

Because `{env:WP_APP_PASSWORD}` reads **one** variable, if you use the *same* name you'd have to keep changing it. Prefer **distinct names** (`WP_APP_PASSWORD_SITE_B`). The only cost is editing one line per project.

---

## Connecting two sites in ONE project (advanced)

If you genuinely want a single opencode session that can reach two sites, define **two MCP servers** with different names:

```json
{
  "mcp": {
    "wordpress_a": {
      "type": "local",
      "command": ["npx", "-y", "@automattic/mcp-wordpress-remote"],
      "environment": {
        "WP_API_URL": "https://site-a.com/wp-json/mcp/mcp-adapter-default-server",
        "WP_API_USERNAME": "ai-agent",
        "WP_API_PASSWORD": "{env:WP_APP_PASSWORD_A}",
        "OAUTH_ENABLED": "false"
      }
    },
    "wordpress_b": {
      "type": "local",
      "command": ["npx", "-y", "@automattic/mcp-wordpress-remote"],
      "environment": {
        "WP_API_URL": "https://site-b.com/wp-json/mcp/mcp-adapter-default-server",
        "WP_API_USERNAME": "ai-agent",
        "WP_API_PASSWORD": "{env:WP_APP_PASSWORD_B}",
        "OAUTH_ENABLED": "false"
      }
    }
  },
  "permission": {
    "wordpress_a_*": "ask",
    "wordpress_b_*": "ask"
  }
}
```

Notes:

- Server names become tool prefixes: `wordpress_a_mcp-adapter-execute-ability`, `wordpress_b_…`.
- Add a `permission` entry **per server** (`wordpress_a_*`, `wordpress_b_*`).
- **Be explicit with the AI** about which site: *"On site B, create a draft…"*. Add a line to `AGENTS.md` reminding it to confirm the target site before writing.

**Trade-off:** convenient for cross-site work, but riskier — it's easy to confuse which site got edited. For client work, prefer *one project per site*.

---

## Using other AI clients

The WordPress side is identical; only the client config differs.

| Client | Where credentials/config go |
|---|---|
| **opencode** | `.opencode/opencode.json` (this guide) |
| **Claude Desktop** | `claude_desktop_config.json` → `mcpServers.wordpress` with the same `WP_API_URL` / username / password |
| **Claude Code** | `claude mcp add` or `.mcp.json` |
| **Cursor** | Settings → MCP → add a server with the same env values |
| **VS Code (Copilot)** | `.vscode/mcp.json` |

All of them use the same proxy command `npx -y @automattic/mcp-wordpress-remote` and the same three env values. The application password is per-site; the AI user is per-site.

---

## Quick reference

| Thing | Where it must be unique per site | Can be shared |
|---|---|---|
| Endpoint URL | ✅ | |
| Application password (and its env var name) | ✅ | |
| AI username | usually `ai-agent` | ✅ (same name is fine) |
| The proxy command `npx -y @automattic/mcp-wordpress-remote` | | ✅ |
| The `permission` block | | ✅ |
| The `ai-office-hours` plugin settings | ✅ (each site its own window/off-day) | |

---

→ Next: [06 — Troubleshooting](06-troubleshooting.md)
