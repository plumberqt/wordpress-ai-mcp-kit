# AI Office Hours

**Time-boxed access for an AI agent on your WordPress site.**

Give your AI assistant the power to edit content *during working hours* — and **automatically lock it to read-only outside them**. Weekly off-days, holidays, and manual override buttons included.

> Part of the [**WordPress AI MCP Kit**](https://github.com/plumberqt/wordpress-ai-mcp-kit). Works standalone too.

---

## Why

If an AI can edit your live site, you want two guarantees:

1. It can only do what a **limited role** allows (an Editor, not an Administrator).
2. It can only do it **when you're around**.

This plugin delivers #2. It forces the AI's WordPress user into a **full-access role during office hours** and a **read-only role the rest of the time** — automatically, on the server, on every request.

---

## Features

- ⏰ **Office-hours window** — e.g. `10:30 – 18:30`, in your site timezone. Overnight windows supported.
- 📅 **Weekly off-day** — e.g. **Wednesday**, locked all day.
- 🎉 **Holidays** — add specific dates for a full-day lock.
- 🔒 **Instant lock** — outside the window the user becomes read-only. No "stale login".
- 🔘 **Manual override** — *Grant access now* / *Revoke access now* / *Resume auto schedule*.
- 🧩 **Capability checkboxes** — control what the "day" role can do (styling & menus, raw HTML, and more — with the dangerous ones off by default).
- 👤 **One target user** — only the AI account is affected; never your admin.
- 🪶 **Lightweight** — one file, no dependencies, no external calls.

---

## Requirements

| | |
|---|---|
| WordPress | **6.0** or newer |
| PHP | **7.4** or newer |

That's it. No other plugins required.

---

## Installation

1. Download [`ai-office-hours.zip`](https://github.com/plumberqt/wordpress-ai-mcp-kit/raw/main/ai-office-hours.zip).
2. WordPress admin → **Plugins → Add New → Upload Plugin** → choose the zip → **Install Now** → **Activate**.
3. Go to **Settings → AI Office Hours**.

---

## Setup (2 minutes)

1. Create (or choose) the **AI user** — an account with role **Editor**, e.g. `ai-agent`.
2. Open **Settings → AI Office Hours**.
3. Set:
   - **Auto switch:** ✅ on
   - **Office window:** `10:30` – `18:30` (your choice)
   - **Weekly off day:** e.g. `Wednesday`
   - **Target user:** `ai-agent`
   - **Day role / Night role:** `ai_day` / `ai_night` (defaults)
4. **Save**.
5. Check **Settings → General → Timezone** is correct (e.g. `Asia/Kolkata`).
6. Add any **holidays** below.

Verify: the status card should read **FULL ACCESS (office hours)** during the window.

---

## How it works

The plugin creates two roles:

| Role | Based on | Powers |
|---|---|---|
| `ai_day` | Editor | Full editing + the extras you tick |
| `ai_night` | — | `read` only (read-only) |

On **every request**, via the `determine_current_user` filter, it checks whether the target user's role matches the schedule and fixes it *before* WordPress checks capabilities. An **hourly WP-Cron** job keeps the database in sync as a backup.

Because the role is corrected per request, there is **no way to hold elevated access past closing time** — not via a cached session, not via a long-running job.

---

## The override buttons

| Button | Effect |
|---|---|
| **Grant access now** | Force full access, ignoring the clock |
| **Revoke access now** | Force locked, ignoring the clock |
| **Resume auto schedule** | Clear the override; clock resumes |

The status card always shows which state you're in:
`FULL ACCESS (office hours)` · `LOCKED (outside office hours)` · `FULL ACCESS (manual grant)` · `LOCKED (manual revoke)` · `AUTO-OFF`.

> Saving the settings form clears any manual override, so the schedule resumes.

---

## FAQ

**Does it touch my admin account?** No. Only the single **target user**.
**What if I set the window wrong?** The status card tells you exactly what state the account is in. Fix and Save.
**Overnight window?** Yes — set an end time earlier than the start (e.g. `22:00`–`06:00`).
**Does it lock holidays in my timezone?** Yes — it uses your site timezone (`wp_timezone()`).
**Will it slow my site?** No — it's a couple of option reads and an in-memory role check per request.

---

## Uninstalling

The `ai_day` / `ai_night` roles and the plugin options remain in the database after deactivation. To clean up fully:

1. Set the target user back to **Editor** (Users → user → Role).
2. Delete the plugin.
3. (Optional) Remove the `ai_day` / `ai_night` roles with a roles-management plugin.

---

## License

GPL-2.0-or-later. See [LICENSE](https://github.com/plumberqt/wordpress-ai-mcp-kit/blob/main/LICENSE).
