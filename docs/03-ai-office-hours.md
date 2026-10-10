# 03 — Configure the AI Office Hours plugin

This is the heart of the safety model. It makes the AI account's powers **follow your clock**.

- **Inside office hours** → the `ai-agent` user gets the **`ai_day`** role (an Editor + any extras you tick).
- **Outside office hours, on the weekly off-day, or on a holiday** → it gets **`ai_night`** = **read-only**.

The plugin re-checks this **on every request**, so the switch is instant — the AI cannot keep elevated access past closing time.

---

## Open the settings

WordPress admin → **Settings → AI Office Hours**.

You'll see a **status card** at the top:

```
Current status: FULL ACCESS (office hours)
Target user: ai-agent (ID 7)  |  Current role: ai_day  |  Window: 10:30 - 18:30  |  Weekly off: Wednesday
[ Grant access now ]  [ Revoke access now ]  [ Resume auto schedule ]
```

---

## The settings, explained

### Auto switch
- **Checked (default):** the schedule controls the role automatically. Leave this on.
- **Unchecked:** the plugin does nothing; the user keeps whatever role it has. Useful only while debugging.

### Office window (Start / End)
- The daily window during which the AI has full access.
- Default: **`10:30` – `18:30`**.
- Times are in your **site timezone** (Settings → General → Timezone). Make sure that's correct — e.g. `Asia/Kolkata` for IST.
- *Edge case:* an end time **earlier** than the start time creates an **overnight window** (e.g. 22:00 – 06:00). That's supported.

### Weekly off day
- One day per week when access is locked **all day**.
- Default: **Wednesday**. Set **No weekly off** to disable.

### Target user
- The account the plugin controls — pick **`ai-agent`**.
- ⚠️ If the dropdown is empty, create the user first ([02 — Create the AI user](02-wordpress-ai-user.md)).
- Only this **one** user's role is ever changed. Your own admin login is never affected.

### Day role / Night role
- **Day role** = `ai_day` (default). **Night role** = `ai_night` (default).
- Leave as-is unless you have a reason to point them at different roles.

### Day-role extra powers
- The `ai_day` role starts as a copy of **Editor**. These checkboxes add (or remove) specific extra capabilities:
  - **Styling & Menus** (`edit_theme_options`) — Customizer, FSE templates, menus. *On by default.*
  - **Raw HTML/JS** (`unfiltered_html`) — *Recommended OFF.* Lets content contain scripts.
  - **Activate/deactivate plugins**, **Install plugins**, **Switch theme**, **Site settings**, **Create users**, **Change roles**, **Delete users** — **all recommended OFF**, especially site settings and user management.
- Tick a box → **Save** → the `ai_day` role is rebuilt instantly.

> **Note:** the `ai_night` role is always just `read` (view dashboard + read content). It can never write.

---

## The three override buttons

The schedule is great, but sometimes you need to open or close the door *right now*.

| Button | What it does | Use when |
|---|---|---|
| **Grant access now** | Forces **full access** (`ai_day`) regardless of time | You need the AI at 9 PM for a quick fix |
| **Revoke access now** | Forces **locked** (`ai_night`) regardless of time | You want the AI to stop, even mid-day |
| **Resume auto schedule** | Clears the manual override; the clock takes over again | When you're done overriding |

> **Important:** saving the *settings form* (times/window/etc.) also clears the manual override, so the schedule resumes. The status card always tells you what state you're in — look for `(manual grant)`, `(manual revoke)`, `AUTO-OFF`, `(office hours)`, or `(outside office hours)`.

---

## Holidays (full-day lock)

Below the settings is the **Holidays** box:

1. Pick a date with the date field.
2. Click **Add holiday**.
3. That whole day, in that timezone, the AI is **locked** — on top of the weekly off-day.
4. Remove any holiday with its **(remove)** link.

Great for public holidays, Diwali week, vacation — any day you don't want the AI touching anything.

---

## Recommended setup (copy this)

| Setting | Value |
|---|---|
| Auto switch | ✅ On |
| Office window | `10:30` – `18:30` (adjust to your day) |
| Weekly off | `Wednesday` (or whichever you prefer) |
| Target user | `ai-agent` |
| Day role / Night role | `ai_day` / `ai_night` |
| Extras | Only **Styling & Menus** (unless you need more) |
| Holidays | Add as they come |

---

## Verify it works (do this once)

1. Make sure the current screen shows **FULL ACCESS (office hours)**.
2. Ask the AI (in opencode) to **create a test draft post** → it should succeed.
3. Now click **Revoke access now**.
4. Ask the AI again → it should get a **`forbidden`** error. 🎉 The lock works.
5. Click **Resume auto schedule**.
6. Delete the test draft.

That's the whole loop, demonstrated in under a minute.

---

## How it works under the hood (for the curious)

- The plugin defines two roles on activation: `ai_day` (Editor clone + ticked extras, minus `unfiltered_html`) and `ai_night` (`read` only).
- It hooks `determine_current_user` (priority 99). Every time WordPress figures out who's logged in, the plugin checks: *is this the target user? is it office hours?* If the role doesn't match what it should be, it fixes it **before** capabilities are checked.
- An **hourly WP-Cron** job does the same sync as a backup, so the database role is always close to correct even between requests.
- **Deactivation** forces the role to its scheduled state, so the account is never left elevated on its own.

---

## Uninstalling

- **Deactivate** → the cron stops and the role is synced to the schedule. The `ai_day`/`ai_night` roles and settings remain in the database.
- **Delete** the plugin → roles and options remain (harmless). If you want a *clean* removal, first set `ai-agent` back to `Editor` manually at Users → `ai-agent`, then delete.

---

→ Next: [04 — Set up opencode + the MCP connection](04-opencode-setup.md)
