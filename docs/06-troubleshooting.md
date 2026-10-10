# 06 — Troubleshooting

Every problem we actually hit while building this, plus the usual suspects. Find your symptom, apply the fix.

---

## Connection

### `opencode mcp list` shows `wordpress` as `error` or `failed`

**Cause:** the proxy process couldn't start — usually npx/network, or Node is missing.

**Fix:**
1. Check Node: `node -v` (must be ≥ 18).
2. Run the proxy by hand to see the real error:
   ```powershell
   npx -y @automattic/mcp-wordpress-remote
   ```
   It should start and wait (that's success — press Ctrl+C). If it errors, fix that first (usually a corporate proxy/registry issue: `npm config get registry`).

### `wordpress` shows `connected` but every call fails with `401`

**Cause:** the credentials never reached WordPress verbatim.

**Checklist:**
- Was the env var set with `setx`, and did you **restart** the editor/terminal after? `setx` only affects *new* processes.
- Verify the var (new terminal): `[Environment]::GetEnvironmentVariable("WP_APP_PASSWORD","User")`
- Is `WP_API_USERNAME` exactly the login (`ai-agent`), not the display name?
- Is `WP_API_URL` the **full endpoint** including `/wp-json/mcp/mcp-adapter-default-server`?
- Did you copy the application password fully (all four groups)?

### Calls fail with `403 Forbidden`

**Cause:** authentication is fine but something blocks it — a security plugin, or the host strips the `Authorization` header.

**Fix:**
1. Temporarily deactivate Wordfence / iThemes / All-In-One Security / similar, retry.
2. If it works, whitelist the `ai-agent` user or the REST route in that plugin.
3. Some hosts (LiteSpeed, some Apache configs) strip Basic auth. Ask the host, or add to `.htaccess`:
   ```apache
   SetEnvIf Authorization "(.*)" HTTP_AUTHORIZATION=$1
   ```

### `404` on the MCP endpoint URL

**Cause:** permalinks are set to **Plain**.

**Fix:** Settings → Permalinks → select **Post name** → Save. REST routes require pretty permalinks. Re-test the endpoint URL — you want a `401`, not a `404`.

---

## Abilities & tools

### The AI says "no abilities" / `discover-abilities` returns nothing

**Cause:** MCP Adapter active but Enable Abilities for MCP not, or everything toggled off.

**Fix:** Confirm both plugins are active, then check **Settings → WP Abilities** — enable the abilities you want.

### A tool exists but the AI can't find "get posts", "create post", etc.

**Cause:** those abilities are toggled off, or the AI is only seeing the 3 meta-tools.

**Fix:** Remember the AI calls **meta-tools** (`discover-abilities`, `get-ability-info`, `execute-ability`). It discovers the rest at runtime. If it seems stuck, tell it: *"Call discover-abilities first."*

### "Ability X has invalid input"

**Cause:** you passed a value the ability's schema rejects — e.g. `order: "desc"` instead of `"DESC"`.

**Fix:** Ask the AI to call `get-ability-info` for that ability to see the exact allowed values, then retry with the correct casing/values.

---

## Office Hours plugin

### The AI still writes after hours

Check, in order:
1. **Target user set?** Settings → AI Office Hours must show the right user.
2. **Right role displayed?** The status card shows the *current* role — it should say `ai_night` / `LOCKED` after hours.
3. **Timezone correct?** Settings → General → Timezone must be your real zone (e.g. `Asia/Kolkata`). A wrong timezone shifts the whole window.
4. **Auto switch** accidentally off?
5. **A manual override** left on (`manual grant`)? Click **Resume auto schedule**.

### The AI can't write even during office hours

1. Status card — is it `FULL ACCESS (office hours)`?
2. Is `ai_night` somehow assigned? Click **Resume auto schedule** or save the settings.
3. Did you uncheck a needed extra (e.g. `edit_theme_options`)? Re-tick and Save.
4. Is `ai-day` role missing? Open **Settings → AI Office Hours** and click **Save** once — it rebuilds the role.

### Feature requests / expected behavior

- **Overrides are cleared when you save the settings form** — by design, so the schedule resumes. If you want a lasting override, don't save the form afterwards.
- **Holidays** only lock the *target user*; your admin account is untouched.

---

## Environment variable issues

### `{env:WP_APP_PASSWORD}` appears literally, or the password is blank

1. The var name must match **exactly** (case-sensitive): `WP_APP_PASSWORD`.
2. It must exist for the **same user and machine** that runs opencode.
3. The app that launches opencode must have been **started after** you set it. Fully restart VS Code (all windows) / terminal.
4. If still stuck, test parity: in a new terminal run
   ```powershell
   echo $env:WP_APP_PASSWORD
   ```
   If it prints the password, opencode should see it too.

### "I set it but PowerShell `setx` said SUCCESS and it still fails"

`setx` writes to the registry for **future** processes only. Close the editor **completely** and reopen. If you launch opencode from inside VS Code's integrated terminal, restart the whole VS Code.

---

## opencode permission prompts

### No prompt appears; actions just run

The `permission` block is missing or mistyped. It must contain `"wordpress_*": "ask"`. Re-copy [`examples/opencode.json`](../examples/opencode.json).

### I clicked "Reject" and now nothing happens

That's correct — a rejected call does nothing. Re-issue the request and choose **Allow once** or **Allow always**.

### "Allow always" is too broad; I want per-action control

Use **Allow once** for writes and **Allow always** only for read tools (list/get/discover). Or remove `"wordpress_*": "ask"` and add specific rules like `"wordpress_mcp-adapter-execute-ability": "ask"` plus per-ability handling in `AGENTS.md`.

---

## Plugin install failures

### "Destination folder already exists"

An old copy is installed. Delete it at **Plugins** (deactivate → delete), then re-upload the zip.

### "The package could not be installed. No valid plugins were found."

The zip's folder structure is wrong. The zip must contain **`ai-office-hours/ai-office-hours.php`** at its root (a folder, then the file). Re-download [`ai-office-hours.zip`](../ai-office-hours.zip) from this repo — it is built correctly.

### "Plugin could not be activated because it triggered a fatal error"

You're likely on PHP < 7.4. Check **Tools → Site Health → Info → Server**. Update PHP.

---

## The nuclear option: start clean

If everything is tangled:

1. Revoke the application password (WordPress → Users → `ai-agent` → Application Passwords → Revoke).
2. Delete `ai-agent` — **but first** set its role back to Editor, or just delete it while logged in as admin.
3. Deactivate & delete the three plugins.
4. Reinstall following [`01`](01-install-plugins.md) → [`04`](04-opencode-setup.md) in order.

Nothing here touches your actual content. Reinstalling the plugins is safe.

---

## Still stuck?

Open an issue on this repository with:
- WordPress version (`Dashboard → At a Glance`)
- PHP version (`Tools → Site Health → Info → Server`)
- The exact error text (from opencode's output)
- The output of `opencode mcp list`

Do **not** paste your application password anywhere.

---

→ Next: [07 — Security notes](07-security.md)
