# 04 — Set up opencode + the MCP connection

Now the client side: install opencode, wire up the MCP server, and add the safety prompts.

---

## Prerequisites

1. **Node.js 18 or newer** — https://nodejs.org (LTS is fine). Verify:
   ```powershell
   node -v
   npm -v
   ```
2. **opencode** — install globally:
   ```powershell
   npm i -g opencode-ai
   ```
   Verify:
   ```powershell
   opencode --version
   ```
3. The **`WP_APP_PASSWORD`** environment variable from [02 — Create the AI user](02-wordpress-ai-user.md), and a **fresh terminal** that can see it.

---

## Where config lives

opencode merges configuration from two places:

| Scope | Path | Use it for |
|---|---|---|
| **Global** | `~/.config/opencode/opencode.json` (Windows: `C:\Users\<you>\.config\opencode\opencode.json`) | Shared stuff — providers, Playwright, common MCP servers |
| **Project** | `<your-project>\.opencode\opencode.json` | The WordPress site for *this* project |

Project config **overrides** global. That's how you point one project at site A and another at site B.

---

## Step 1 — Create the project config

In the folder where you run opencode, create `.opencode/opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "wordpress": {
      "type": "local",
      "command": ["npx", "-y", "@automattic/mcp-wordpress-remote"],
      "enabled": true,
      "timeout": 30000,
      "environment": {
        "WP_API_URL": "https://YOUR-SITE.com/wp-json/mcp/mcp-adapter-default-server",
        "WP_API_USERNAME": "ai-agent",
        "WP_API_PASSWORD": "{env:WP_APP_PASSWORD}",
        "OAUTH_ENABLED": "false"
      }
    }
  },
  "permission": {
    "wordpress_*": "ask",
    "bash": {
      "*": "ask",
      "rm *": "deny",
      "del *": "deny",
      "rmdir *": "deny",
      "Remove-Item *": "deny",
      "format *": "deny"
    },
    "external_directory": "ask",
    "webfetch": "ask"
  }
}
```

**Edit only what's marked:**

| Key | Change to |
|---|---|
| `WP_API_URL` | Your site's endpoint: `https://YOUR-SITE.com/wp-json/mcp/mcp-adapter-default-server` |
| `WP_API_USERNAME` | `ai-agent` (or whatever you named the user) |
| `WP_API_PASSWORD` | **Leave as `{env:WP_APP_PASSWORD}`** — this reads your OS variable. Never paste the real password here. |

> A ready copy is at [`examples/opencode.json`](../examples/opencode.json).

### What each field means

- `"type": "local"` → opencode launches a local command as the MCP server.
- `"command": ["npx", "-y", "@automattic/mcp-wordpress-remote"]` → runs the proxy (no global install needed).
- `"timeout": 30000` → 30 s per call. Increase if your host is slow.
- `OAUTH_ENABLED: "false"` → we use the application password, not OAuth.

### What the `permission` block does

- `"wordpress_*": "ask"` → **every** WordPress tool call (the server is named `wordpress`) shows an **Allow once / Allow always / Reject** prompt. This is your seatbelt.
- The `bash` rules let opencode run normal commands but **hard-deny destructive ones** (`rm`, `del`, `Remove-Item`, `format`).
- `"webfetch": "ask"` → asks before fetching URLs.

---

## Step 2 — Add the AI's rules file

Create `.opencode/AGENTS.md` (a ready copy is at [`examples/AGENTS.md`](../examples/AGENTS.md)):

```markdown
# WordPress rules

Connected via the `wordpress` MCP.

## Hard rules
1. Never delete anything. If asked to "remove", unpublish/draft it instead.
2. Never publish. Always create/update as draft, show me the summary, wait for approval.
3. Never touch theme files, plugin files, .htaccess, wp-config.php, users, roles, settings.
4. Never install/activate anything.
5. Never change site URL, timezone, or permalinks.

## How to work
- New content → create as draft, then report what changed.
- Edits → report post title + which sections changed.
- If a tool returns `forbidden` → office hours are over. Stop. Do not retry.
  Tell me to use "Grant access now" in Settings → AI Office Hours.
```

opencode reads this automatically and folds it into the AI's instructions every session.

---

## Step 3 — Restart everything

Because `WP_APP_PASSWORD` was set with `setx`, **any already-open app can't see it**. So:

1. Close opencode.
2. **Fully close your editor** (VS Code: close *all* windows, not just the tab) and the terminal.
3. Open a **new** terminal and `cd` into your project.
4. Run:
   ```powershell
   opencode mcp list
   ```

**Expected:**

```
┌  MCP Servers
│
●  ✓ wordpress connected
│      npx -y @automattic/mcp-wordpress-remote
│
└  1 server(s)
```

`connected` means opencode started the proxy and listed its tools. It does **not** yet prove your password is right (that's checked on the first real call).

---

## Step 4 — First real call (this is the moment of truth)

1. Start opencode in the project:
   ```powershell
   opencode
   ```
2. Type:
   > **List recent posts from WordPress.**
3. opencode will try to call a `wordpress_*` tool and **show a permission prompt**:
   ```
   ⚑ wordpress_mcp-adapter-execute-ability
   Allow once / Allow always / Reject
   ```
   Press **Allow always** for read tools (or **Allow once** while testing).
4. If the connection works you'll get a list of posts (or an empty list if the site has none — still a success).

### Then test a write

> **Create a test draft post titled "MCP Test".**

- **Allow once** → the draft appears in wp-admin → **Posts**.
- Delete it when done.

### Then test the lock (optional but recommended)

1. In **Settings → AI Office Hours**, click **Revoke access now**.
2. Ask opencode to create another draft → you should get **`forbidden`**.
3. Click **Resume auto schedule**.

---

## Everyday use

- opencode prompts **per call**. Choose:
  - **Allow once** — for anything that writes (creates/updates content). Safest.
  - **Allow always** — comfortable for pure read tools during a session.
  - **Reject** — cancel.
- When the office-hours window closes, writes just start returning `forbidden`. No config change needed — that's the plugin doing its job.

---

## Common config gotchas

| Symptom | Cause | Fix |
|---|---|---|
| `wordpress` shows `error` in `mcp list` | npx can't fetch the package (no internet / proxy) | Run `npx -y @automattic/mcp-wordpress-remote` manually to see the error |
| First call returns `401` | Password wrong, or env var not visible to opencode | Recheck the env var in a **new** terminal; restart the editor |
| First call returns `403` | Security plugin/host blocks Basic auth | See [06 — Troubleshooting](06-troubleshooting.md) |
| `{env:WP_APP_PASSWORD}` shows literally | opencode too old, or var misspelled | Update opencode; confirm the var name is exact |
| Prompt never appears, call runs silently | `permission` block missing/typo'd | Re-copy the config; it must have `"wordpress_*": "ask"` |

---

→ Next: [05 — Connect multiple websites](05-multiple-sites.md)
