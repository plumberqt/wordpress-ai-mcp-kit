<div align="center">

# WordPress AI MCP Kit

**Connect an AI coding assistant (opencode, Claude, Cursor, VS Code — anything MCP) to your WordPress site — safely, time-boxed, and fully under your control.**

[![WordPress](https://img.shields.io/badge/WordPress-6.9%2B-21759b)](https://wordpress.org/)
[![PHP](https://img.shields.io/badge/PHP-7.4%2B-777bb4)](https://www.php.net/)
[![MCP](https://img.shields.io/badge/MCP-compatible-6e56cf)](https://modelcontextprotocol.io/)
[![License: GPLv2+](https://img.shields.io/badge/License-GPLv2%2B-blue)](LICENSE)

</div>

---

## What is this?

This is a **complete, copy-paste kit** that lets an AI agent (like the one inside opencode / Claude Desktop / Cursor) manage your WordPress content over **MCP (Model Context Protocol)** — create drafts, edit posts, fix SEO meta, upload images, moderate comments — while you keep **hard control over what it can and cannot do**.

It ships three things:

1. **A setup guide** (this repo) — every plugin, every link, every tiny step, every error and its fix.
2. **`ai-office-hours`** — a free WordPress plugin (ours) that **automatically locks the AI account outside your working hours** (e.g. 10:30 AM – 6:30 PM, Wednesday off, holidays).
3. **Ready-to-use config templates** for opencode with an **"ask before every action"** safety layer.

> **Why?** Giving an AI a live site is powerful — and scary. This kit makes it powerful *and* safe: the AI works as a **normal, low-privilege WordPress user**, only during **your office hours**, and **you approve every single tool call**.

---

## Table of contents

- [How it works (the big picture)](#how-it-works-the-big-picture)
- [Components & download links](#components--download-links)
- [Quick start](#quick-start)
- [Repository contents](#repository-contents)
- [The safety model (three layers)](#the-safety-model-three-layers)
- [FAQ](#faq)
- [License](#license)

---

## How it works (the big picture)

```
 ┌─────────────────────┐        MCP (HTTP)         ┌──────────────────────────────┐
 │   Your AI client    │  ──────────────────────▶  │        WordPress site        │
 │  (opencode / Claude │                           │                              │
 │   / Cursor / VS Code│  ◀──────────────────────  │  /wp-json/mcp/               │
 │        …)           │        JSON over HTTPS    │    mcp-adapter-default-server│
 └─────────────────────┘                           └──────────────────────────────┘
          │                                                     ▲
          │ runs                                                │
          ▼                                                     │ exposes
 ┌─────────────────────┐                           ┌──────────────────────────────┐
 │ mcp-wordpress-remote│                           │   MCP Adapter (plugin)       │
 │ (npm proxy, STDIO)  │                           │   bridges Abilities ⇄ MCP    │
 └─────────────────────┘                           └──────────────────────────────┘
                                                                ▲
                                                                │ registers abilities
                                                   ┌──────────────────────────────┐
                                                   │ Enable Abilities for MCP     │
                                                   │ (content, SEO, menus, media…)│
                                                   └──────────────────────────────┘
                                                                ▲
                                                                │ governs the account
                                                   ┌──────────────────────────────┐
                                                   │ AI Office Hours (this kit)   │
                                                   │ day role ⇄ read-only lock    │
                                                   └──────────────────────────────┘
```

**The chain, in words:**

1. WordPress 6.9+ ships the **Abilities API** — a standard way to register "things a plugin can do".
2. The official **MCP Adapter** plugin turns those abilities into **MCP tools** and serves them at a REST endpoint: `https://your-site.com/wp-json/mcp/mcp-adapter-default-server`.
3. **Enable Abilities for MCP** registers ~100 ready-made abilities (posts, pages, SEO, menus, media, comments…) and gives you a **dashboard to toggle each one**.
4. **AI Office Hours** (ours) forces the AI's WordPress account into the right **role** based on the clock — full access in office hours, read-only outside.
5. Your AI client talks to the endpoint through the **`mcp-wordpress-remote`** proxy using an **Application Password**.
6. opencode's **permission rules** make it prompt you **before every WordPress action**.

---

## Components & download links

Everything you need, with links and what each piece actually does.

### 1. MCP Adapter — *by WordPress.org (official)*

| | |
|---|---|
| **What it does** | Bridges the WordPress Abilities API to MCP. Creates the server endpoint your AI connects to. |
| **Install from** | WordPress Admin → **Plugins → Add New** → search **"MCP Adapter"** |
| **WordPress.org** | https://wordpress.org/plugins/mcp-adapter/ |
| **GitHub** | https://github.com/WordPress/mcp-adapter |
| **Direct zip (latest)** | https://github.com/WordPress/mcp-adapter/releases/latest/download/mcp-adapter.zip |
| **Requires** | WordPress **6.9+**, PHP **7.4+** |

### 2. Enable Abilities for MCP — *by Fabio Montenegro*

| | |
|---|---|
| **What it does** | Registers ~102 content-management abilities (posts, pages, categories, tags, comments, media, users, menus, SEO for Rank Math/Yoast/AIOSEO/SEOPress, WooCommerce, JetEngine, cache purge…) and gives you **per-ability on/off toggles** + an **activity log**. This is the plugin that actually gives the AI useful powers. |
| **Install from** | WordPress Admin → **Plugins → Add New** → search **"Enable Abilities for MCP"** → then open **Settings → WP Abilities** |
| **WordPress.org** | https://wordpress.org/plugins/enable-abilities-for-mcp/ |
| **GitHub** | https://github.com/FabioMontenegro/enable-abilities-for-mcp |
| **Requires** | WordPress **6.9+**, PHP **8.0+**, and **MCP Adapter** active |

### 3. AI Office Hours — *this kit (ours)*

| | |
|---|---|
| **What it does** | Forces the AI's WordPress user into a **"day" role during office hours** and a **read-only "night" role outside** them. Weekly off-day + holiday list + manual **Grant / Revoke / Resume** buttons. |
| **Download** | [`ai-office-hours.zip`](ai-office-hours.zip) (in this repo) |
| **Source** | [`plugin/ai-office-hours/`](plugin/ai-office-hours/) |
| **Docs** | [`plugin/ai-office-hours/README.md`](plugin/ai-office-hours/README.md) |
| **Requires** | WordPress **6.0+**, PHP **7.4+** |
| **License** | GPL-2.0-or-later |

### 4. `@automattic/mcp-wordpress-remote` — *npm proxy, by Automattic*

| | |
|---|---|
| **What it does** | A small local program that translates between your AI client (STDIO) and your WordPress shell (HTTP). Handles authentication. |
| **Install** | No install needed — run with `npx -y @automattic/mcp-wordpress-remote` |
| **npm** | https://www.npmjs.com/package/@automattic/mcp-wordpress-remote |
| **GitHub** | https://github.com/Automattic/mcp-wordpress-remote |
| **Requires** | Node.js **18+** |

### 5. opencode — *the AI client used in this guide*

| | |
|---|---|
| **What it does** | The command-line AI coding assistant. Reads the config, connects the MCP server, asks you before each action. |
| **Website** | https://opencode.ai |
| **Install** | `npm i -g opencode-ai` (or see opencode.ai/docs) |
| **Requires** | Node.js **18+** |

> **Any MCP client works.** Claude Desktop, Cursor, VS Code Copilot, Windsurf — just point them at the same endpoint with the same application password. This repo uses opencode because it has the cleanest **per-tool "ask" permissions**.

---

## Quick start

> Full, screenshot-level detail for **every** step is in [`docs/`](docs/). Here is the 30-second overview.

**On your WordPress site:**

1. Install & activate **MCP Adapter** (Plugins → Add New → "MCP Adapter").
2. Install & activate **Enable Abilities for MCP** (Plugins → Add New → "Enable Abilities for MCP").
3. Create a dedicated user **`ai-agent`** with role **Editor** (Users → Add New).
4. Edit `ai-agent` → scroll to **Application Passwords** → name it `opencode` → **Add New** → copy the password (`xxxx xxxx xxxx xxxx`).
5. Upload & activate **`ai-office-hours.zip`** → **Settings → AI Office Hours** → set the window (e.g. 10:30–18:30), weekly off (Wednesday), target user (`ai-agent`).

**On your computer:**

6. Install Node.js 18+ and opencode.
7. Save the application password as an environment variable:
   ```powershell
   setx WP_APP_PASSWORD "xxxx xxxx xxxx xxxx"
   ```
8. Copy [`examples/opencode.json`](examples/opencode.json) into your project's `.opencode/opencode.json` and edit the site URL + username.
9. **Restart** your editor/terminal, then verify:
   ```
   opencode mcp list
   ```
   You should see `wordpress ✓ connected`.

**Detailed guides:**

| Step | Guide |
|---|---|
| Understand the whole thing | [docs/00-understanding.md](docs/00-understanding.md) |
| Install the WordPress plugins | [docs/01-install-plugins.md](docs/01-install-plugins.md) |
| Create the AI user + app password | [docs/02-wordpress-ai-user.md](docs/02-wordpress-ai-user.md) |
| Configure AI Office Hours | [docs/03-ai-office-hours.md](docs/03-ai-office-hours.md) |
| Set up opencode + MCP | [docs/04-opencode-setup.md](docs/04-opencode-setup.md) |
| Connect **multiple** websites | [docs/05-multiple-sites.md](docs/05-multiple-sites.md) |
| Fix problems (troubleshooting) | [docs/06-troubleshooting.md](docs/06-troubleshooting.md) |
| Security notes | [docs/07-security.md](docs/07-security.md) |

---

## Repository contents

```
wordpress-ai-mcp-kit/
├── README.md                     ← you are here
├── LICENSE                       ← GPL-2.0
├── ai-office-hours.zip           ← the ready-to-install plugin (upload this in WP)
├── plugin/
│   └── ai-office-hours/
│       ├── ai-office-hours.php   ← plugin source
│       ├── README.md             ← plugin documentation (GitHub)
│       └── readme.txt            ← plugin documentation (WordPress standard)
├── docs/
│   ├── 00-understanding.md       ← how the whole system fits together
│   ├── 01-install-plugins.md     ← every plugin + link + install steps
│   ├── 02-wordpress-ai-user.md   ← dedicated user + application password
│   ├── 03-ai-office-hours.md     ← office-hours plugin setup
│   ├── 04-opencode-setup.md      ← MCP config, env var, permissions
│   ├── 05-multiple-sites.md      ← connect many websites
│   ├── 06-troubleshooting.md     ← every error we hit + fix
│   └── 07-security.md            ← hardening notes
└── examples/
    ├── opencode.json             ← ready config (edit 3 values)
    ├── AGENTS.md                 ← AI safety rules
    └── site-switch-template.jsonc← copy for each new site
```

---

## The safety model (three layers)

The AI can only do what **all three** layers allow. Blast radius is tiny by design.

| Layer | Where | What it stops |
|---|---|---|
| **1. Server capabilities** | WordPress roles (via AI Office Hours) | The AI account is an **Editor**, never an Administrator. Outside office hours it can **only read**. It physically **cannot** touch theme files, plugins, `.htaccess`, `wp-config.php`, users, or settings — those abilities don't exist for it. |
| **2. Office-hours lock** | AI Office Hours plugin | Outside the window / on the weekly off-day / on holidays the AI user is **auto-downgraded to read-only**. Even if everything else fails, it can't write at night. |
| **3. Client prompt** | opencode `permission` rules | Every WordPress tool call pops **once / always / reject**. Nothing happens without you watching. |

Plus a **4th safety habit**: `DISALLOW_FILE_EDIT` in `wp-config.php` disables the built-in theme/plugin code editor entirely.

And the AI's own rules file ([`examples/AGENTS.md`](examples/AGENTS.md)) tells it: *always create drafts, never publish without approval, never delete, stop on `forbidden`.*

---

## FAQ

**Do I need to expose my site publicly?** It already is — this is the same HTTPS REST API WordPress uses for apps. No extra port, no SSH, no FTP. The AI authenticates with an Application Password, exactly like a mobile app would.

**Is the application password safe in plain text?** It never goes in a file. This guide stores it in an OS **environment variable** (`WP_APP_PASSWORD`) and references it as `{env:WP_APP_PASSWORD}`. The config you commit contains **no secret**.

**Can I revoke access instantly?** Yes — three ways: (1) click **Revoke** in AI Office Hours, (2) let the office-hours window close, (3) delete the Application Password in WordPress. All take effect on the very next request.

**Which SEO plugin is supported?** The AI can read/write meta for **Rank Math, Yoast SEO, All in One SEO (AIOSEO), and SEOPress** — whichever you have active. Only the matching abilities appear.

**Will this work on cheap shared hosting?** Yes, as long as WordPress is **6.9+** and PHP is **7.4+** (8.0+ recommended). No server config needed.

**Does it work with multiple sites?** Yes — see [docs/05-multiple-sites.md](docs/05-multiple-sites.md). One config block per site.

---

## License

This kit (including the `ai-office-hours` plugin) is released under the **GNU General Public License v2.0 or later** — the same license WordPress itself uses. See [LICENSE](LICENSE).

MCP Adapter is GPL-2.0-or-later (© WordPress.org Contributors). Enable Abilities for MCP is GPL-2.0-or-later (© Fabio Montenegro). `mcp-wordpress-remote` is MIT (© Automattic). Those projects keep their own licenses.
