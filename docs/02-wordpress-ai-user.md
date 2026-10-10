# 02 — Create the AI user & application password

The AI must **not** use your admin account. It gets its own account with the **Editor** role. Even before Office Hours kicks in, this account cannot touch themes, plugins, settings, or users.

---

## Step 1 — Create the `ai-agent` user

1. WordPress admin → **Users → Add New**.
2. Fill in:
   - **Username:** `ai-agent`
     *(Keep it exactly `ai-agent` — the Office Hours plugin looks for this name on activation. You can change it later, it's not mandatory.)*
   - **Email:** any address you control, e.g. `ai-agent@your-site.com`. It won't receive mail; it's just a required field.
   - **Password:** click **Show password** and save it somewhere safe. Actually, you'll barely use this login — the AI uses an *application password* instead. Still, keep it.
   - **Role:** **Editor**
     ⚠️ **Not Administrator.** Editor can manage posts, pages, media, comments — but cannot touch plugins, themes, users, or settings.
   - **First / Last name:** e.g. `AI Agent` (optional but tidy).
3. Click **Add New User**.

> **Why Editor and not Author?** Author can only touch their own posts. Editor is a good middle ground and is exactly what the Office Hours plugin upgrades/downgrades. If you want tighter control, use Author — the plugin still works.

---

## Step 2 — Create its Application Password

An **Application Password** is a special password that WordPress generates for apps (mobile apps, scripts, this AI). It bypasses two-factor prompts, it's **revocable on its own**, and it doesn't reveal your real login password.

1. Still in **Users**, click the **`ai-agent`** user to edit it (or hover the user row → **Edit**).
2. Scroll to the bottom of the profile page.
3. Find the section **Application Passwords**.
   - If you don't see it, see the note at the bottom of this page.
4. In the **New Application Password Name** box, type: `opencode`
   (The name is just a label so you can recognise/revoke it later. Use a different name per tool/site, e.g. `opencode-laptop`, `claude-desktop`.)
5. Click **Add New Application Password**.
6. WordPress shows the password **once**, in a green box, formatted in groups of four:
   ```
   abcd efgh ijkl mnop
   ```
7. **Copy it immediately** and paste it somewhere safe (a password manager, or straight into the environment variable in the next step). **You cannot see it again.**

> **Spaces matter? No.** WordPress shows spaces for readability. Whether you keep or remove the spaces, the same password works. We keep them — both `wp-cli` and the MCP proxy handle them fine.

---

## Step 3 — (Recommended) Save it as an environment variable

Never paste this password into a config file you might commit to git. Instead, store it in your **operating system** and reference it by name.

### Windows (PowerShell)

```powershell
setx WP_APP_PASSWORD "abcd efgh ijkl mnop"
```

- Replace `abcd efgh ijkl mnop` with **your** real application password.
- `setx` saves it permanently for your Windows **user account**.
- ⚠️ **New processes only:** any already-open app (VS Code, terminal) won't see it until you **restart that app**. (This bites people later — remember it.)

Verify it was saved (open a **new** terminal):

```powershell
[Environment]::GetEnvironmentVariable("WP_APP_PASSWORD","User")
```

### macOS / Linux

Add to your shell profile (`~/.zshrc` or `~/.bashrc`):

```bash
export WP_APP_PASSWORD="abcd efgh ijkl mnop"
```

Then reload: `source ~/.zshrc`.

> **Multiple sites?** Give each site its own variable: `WP_APP_PASSWORD_SITE2`, `WP_APP_PASSWORD_CLIENT1`, … See [05 — Multiple sites](05-multiple-sites.md).

---

## Step 4 — Test the login (optional but smart)

Before wiring up the AI, prove the credentials work with a simple request.

### PowerShell

```powershell
$user = "ai-agent"
$pass = $env:WP_APP_PASSWORD
$pair = "${user}:${pass}"
$b64  = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes($pair))
Invoke-RestMethod `
  -Uri "https://your-site.com/wp-json/wp/v2/users/me" `
  -Headers @{ Authorization = "Basic $b64" }
```

### macOS / Linux / WSL

```bash
curl -s -u "ai-agent:$WP_APP_PASSWORD" \
  https://your-site.com/wp-json/wp/v2/users/me
```

**Expected:** a JSON object with `"slug":"ai-agent"` and its roles.

- If you get your user back → ✅ credentials are perfect, continue.
- `401` → wrong username/password, or the app password wasn't copied fully.
- `403` → a security plugin or server rule is blocking Basic auth; see [06 — Troubleshooting](06-troubleshooting.md).

---

## "I don't see the Application Passwords section!"

Common causes, in order of likelihood:

1. **Your site isn't HTTPS.** WordPress only shows Application Passwords on HTTPS sites. Fix: install an SSL certificate (most hosts give one free via Let's Encrypt).
2. **A security plugin hides it** (Wordfence, iThemes, etc.), or disables app passwords. Temporarily deactivate it, create the password, then re-enable.
3. **You're editing your own profile, not `ai-agent`.** Application Passwords appear on **every** user's profile page.
4. **A hosting rule / `.htaccess` strips the `Authorization` header.** Ask your host, or add the standard `SetEnvIf Authorization` line.

---

## Revoking access later

- **WordPress admin → Users → `ai-agent` → Application Passwords** → click **Revoke** next to `opencode`.
- The AI loses access on the **next request**. Nothing else to clean up.

You can also create a *second* one for testing and revoke it without touching the first.

---

→ Next: [03 — Configure AI Office Hours](03-ai-office-hours.md)
