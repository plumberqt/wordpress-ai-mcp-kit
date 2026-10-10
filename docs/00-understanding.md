# 00 — Understanding the whole system

Read this once. Everything else in this repo is just *doing* what this page explains.

---

## The problem

An AI assistant is great at content work: writing drafts, fixing meta descriptions, resizing image alt text, moderating comments. But to do that on WordPress it needs access — and "give an AI your admin login" is a terrible idea. It could delete everything, leak data, or break the site at 3 AM.

## The solution

Give the AI a **normal, low-privilege WordPress account**, connect it through a **standard, revocable protocol (MCP)**, and wrap it in **three independent safety layers**. Then you get the power without the fear.

---

## The pieces, from the ground up

### 1. Abilities API (inside WordPress 6.9+)

WordPress 6.9 introduced the **Abilities API**. Think of it as a clean menu of "things this site can do":

```
core/get-site-info        → read site details
ewpa/get-posts            → list posts
ewpa/create-post          → create a post
ewpa/update-post          → edit a post
ewpa/get-rankmath         → read Rank Math SEO meta
...
```

Every ability declares **who is allowed to run it** (capability checks) and **what input it accepts**. Nothing is exposed by default.

### 2. MCP Adapter (official plugin)

MCP Adapter takes that menu and serves it over **MCP** — the "Model Context Protocol", a standard language AI tools speak. It creates one HTTPS endpoint:

```
https://YOUR-SITE.com/wp-json/mcp/mcp-adapter-default-server
```

The client doesn't call each ability directly. It calls **three meta-tools**:

- `mcp-adapter/discover-abilities` — *"what can you do?"*
- `mcp-adapter/get-ability-info` — *"how do I use this one?"*
- `mcp-adapter/execute-ability` — *"run this one with these inputs"*

### 3. Enable Abilities for MCP

This is the plugin that **registers the actual useful abilities** (about 102 of them): posts, pages, categories, tags, comments, media, menus, users, SEO (Rank Math / Yoast / AIOSEO / SEOPress), WooCommerce, JetEngine, cache purge, llms.txt, and more.

It also gives you **Settings → WP Abilities**, where you can switch any of them off. Turn off everything you don't need — fewer abilities = smaller attack surface.

### 4. AI Office Hours (this kit)

WordPress roles are normally static. This plugin makes the AI user's role **time-dependent**:

- **Inside office hours** → `ai_day` role = an Editor (plus whatever extras you tick).
- **Outside office hours** → `ai_night` role = **read-only**.
- **Wednesday / holidays** → locked all day.

It works by hooking `determine_current_user`, so the role is corrected **on every request** before WordPress checks capabilities. The AI can't "stay logged in" past 6:30 PM.

### 5. `mcp-wordpress-remote` (the proxy)

Your AI client (opencode) usually speaks **STDIO** (local subprocess). WordPress speaks **HTTP**. This tiny npm program bridges the two and injects your credentials. You never install it globally — `npx` fetches it on demand.

### 6. The AI client (opencode)

The client:
- Reads `.opencode/opencode.json` to know the endpoint and credentials.
- Reads `.opencode/AGENTS.md` for behavioral rules.
- **Asks you before every WordPress action** (because of the `permission` block).

---

## One request, end to end

When you type *"create a draft post about X"* in opencode:

```
you ──▶ opencode
          │ 1. builds an MCP tool call: execute-ability(ewpa/create-post, {...})
          │ 2. permission rule "wordpress_*": "ask"  → shows you a prompt
          ▼    (you click "Once")
        mcp-wordpress-remote  (local proxy, adds Basic auth = ai-agent : app-password)
          │ 3. HTTP POST over HTTPS
          ▼
        https://your-site/wp-json/mcp/mcp-adapter-default-server
          │ 4. WordPress resolves the user (determine_current_user)
          │    └─ AI Office Hours forces role = ai_day  (it's 11 AM)  ✔
          │ 5. ability checks capability: does ai_day have edit_posts? yes
          ▼
        post created as draft  ──▶ JSON back to opencode ──▶ shown to you
```

Now the same request at **8 PM**:

```
          │ 4. AI Office Hours forces role = ai_night  (read-only)
          │ 5. capability edit_posts  →  DENIED
          ▼
        { "error": "forbidden" }  ──▶  opencode tells you: office hours over.
```

No file was touched. No setting changed. The door was simply not unlocked.

---

## Why each safety layer matters

| If this fails… | …this still protects you |
|---|---|
| AI hallucinates a destructive command | **AI Office Hours** blocks writes outside hours |
| AI runs during office hours but does something dumb | **WordPress capabilities** — it's only an Editor, no admin powers |
| Everything else is misconfigured | **opencode** still asks you before each call |

Defense in depth: you'd have to defeat all three at once.

---

## What the AI can NEVER do here

By design, the abilities list contains **no** way to:

- edit theme files, plugin files, or code
- read/write `wp-config.php` or `.htaccess`
- install/activate/delete plugins
- create users or change roles
- change site URL, timezone, permalinks

If you ever want the AI to do one of those, you do it yourself in wp-admin. The AI is a **content worker**, not a sysadmin.

---

→ Next: [01 — Install the WordPress plugins](01-install-plugins.md)
