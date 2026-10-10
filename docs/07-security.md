# 07 — Security notes

This guide already makes the AI account safe by default. These notes explain *why*, and how to tighten it further.

---

## The principles

1. **Least privilege** — the AI is an Editor, never an Administrator.
2. **Least time** — writes only happen inside office hours.
3. **Least ability** — only the abilities you explicitly enable exist for the AI.
4. **Human in the loop** — you approve every action.
5. **No secrets in files** — the password lives in an OS environment variable.
6. **Revocable** — one click kills access.

---

## The four layers, again

| Layer | Where | Defeated by |
|---|---|---|
| Role capabilities | WordPress (`ai-agent` = Editor) | An admin promoting it — don't |
| Office hours | `ai-office-hours` plugin | Turning auto-switch off — don't |
| Per-tool prompt | opencode `permission` | Removing `"wordpress_*": "ask"` — don't |
| No file editing | `DISALLOW_FILE_EDIT` | Editing `wp-config.php` to remove it — don't |

You'd have to disable all four to be reckless. Don't.

---

## Harden `wp-config.php` (recommended)

Disable the built-in theme/plugin code editor. Add **above** the line `/* That's all, stop editing! */`:

```php
/* Disable the plugin/theme file editor in wp-admin */
define( 'DISALLOW_FILE_EDIT', true );
```

Optional extras:

```php
/* Block anyone from installing/updating plugins & themes from wp-admin */
define( 'DISALLOW_FILE_MODS', true );

/* Force admin over HTTPS (only if your whole site is HTTPS) */
define( 'FORCE_SSL_ADMIN', true );

/* Turn off the XML-RPC attack surface (only if you don't use the app) */
add_filter( 'xmlrpc_enabled', '__return_false' );
```

> **How to edit `wp-config.php`:** via your host's File Manager or SFTP. **Back it up first.** The three `define()` lines go with the other `define()` lines, before the "stop editing" comment. (The AI cannot and must not do this — you do it.)

---

## The application password

- **Scope:** it grants full access **as that one user** — nothing more. If the user can't do it, neither can the password.
- **Revocable:** WordPress → Users → `ai-agent` → Application Passwords → **Revoke**.
- **Named:** use a clear name (`opencode-laptop`) so you know what a revoke kills.
- **Never:** don't email it, don't commit it, don't paste it in a chat/screenshot. If you ever do, **revoke and regenerate**.
- **Per site, per tool:** a separate one for each site and each client. Then revoking one never affects others.

### If you must keep it on disk

Prefer the OS env var (`setx`). If you truly need a file, put it **outside** any git repo and reference it with `{file:...}` if your client supports it — never inline in `opencode.json`.

---

## What the AI can never reach (by design)

No enabled ability can:

- read or write `wp-config.php`, `.htaccess`, or any theme/plugin file
- install, activate, update, or delete plugins/themes
- create users, change roles, or edit profiles
- change site URL, timezone, permalinks, or general settings

If you ever *want* it to do one of these, come back and enable the specific ability deliberately — and expect to justify it.

---

## Trim the attack surface

In **Settings → WP Abilities**:

- Turn **off** every ability you don't use.
- Especially **off**: user management, role changes, code snippets, delete-* abilities, translation creation, raw post-meta writes.
- Keep reads + the few writes you actually need (create/update post, upload image, SEO meta, clear cache).

Fewer abilities = fewer ways for a confused model to do something unexpected.

---

## Activity log

**Enable Abilities for MCP** includes an **activity log** — every ability execution recorded under the real WordPress user. Check it periodically:

- **Settings → WP Abilities** (log tab), or wherever the plugin exposes it for your version.

It's your audit trail: *what ran, when, as whom.*

---

## The `AGENTS.md` behavior contract

Files like [`examples/AGENTS.md`](../examples/AGENTS.md) tell the model what *not* to do even when it technically could:

- always draft, never publish without approval
- never delete
- stop on `forbidden`

Treat it as a **guideline**, not a security boundary — the real boundaries are the WordPress role and the permission prompts. But a good `AGENTS.md` prevents 95% of accidental misbehavior.

---

## Multi-site caution

When you connect several sites in one session ([05](05-multiple-sites.md)), the risk is **confusion**, not intrusion. Make the AI state the target site before any write, and prefer **one project per site** for client work.

---

## Incident response — "something looks wrong"

1. **Stop:** click **Revoke access now** in AI Office Hours (instant).
2. **Revoke the password:** WordPress → Users → `ai-agent` → Application Passwords → Revoke.
3. **Check the log:** Settings → WP Abilities activity log.
4. **Check content:** Posts/Pages/Media for anything unexpected; restore drafts/deletions.
5. **Rotate:** when you're back, create a **new** application password and a **new** env var value; update the config.
6. **Review:** tighten abilities and office hours before reconnecting.

---

## Quick security checklist

- [ ] AI uses a **separate `ai-agent` account**, role **Editor**
- [ ] Application Password named clearly, stored in **env var** (`WP_APP_PASSWORD`)
- [ ] `WP_APP_PASSWORD` is **not** written in any file you commit
- [ ] `DISALLOW_FILE_EDIT` is **true** in `wp-config.php`
- [ ] AI Office Hours: **auto on**, correct **timezone**, **target user** set, weekly off + holidays set
- [ ] **Settings → WP Abilities**: only needed abilities enabled; delete/user/code abilities **off**
- [ ] `permission`: `"wordpress_*": "ask"` present
- [ ] You know where the three **revoke** switches are

---

→ Back to [README](../README.md)
