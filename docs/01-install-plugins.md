# 01 — Install the WordPress plugins

You will install **three** plugins. Everything is free and from trusted sources.

> **Before you start — check your versions.**
> Open your WordPress admin → **Tools → Site Health → Info → Server**, or just Dashboard → **At a Glance**.
> You need **WordPress 6.9 or newer**. For the abilities plugin you also want **PHP 8.0+**.
> If WordPress is older, update it first (Dashboard → Updates).

The three plugins, in the order you should install them:

| Order | Plugin | Why |
|---|---|---|
| 1 | **MCP Adapter** | Creates the MCP server endpoint |
| 2 | **Enable Abilities for MCP** | Registers the content abilities |
| 3 | **AI Office Hours** | Time-boxes the AI account (this kit) |

---

## Plugin 1 — MCP Adapter (official WordPress plugin)

**Source:** https://wordpress.org/plugins/mcp-adapter/
**GitHub:** https://github.com/WordPress/mcp-adapter

### Install from the dashboard (easiest)

1. Log in to WordPress admin (`https://your-site.com/wp-admin`).
2. In the left menu click **Plugins → Add New**.
3. In the search box (top right) type: **`MCP Adapter`**
4. The first result is *"MCP Adapter"* by **WordPress.org Contributors**.
   - ⚠️ Make sure the author says **WordPress.org Contributors**. There are copycat plugins.
5. Click **Install Now**, wait for it to finish, then click **Activate**.

### Install from a zip (if search fails)

1. Download the latest release: https://github.com/WordPress/mcp-adapter/releases/latest/download/mcp-adapter.zip
2. In WordPress go to **Plugins → Add New → Upload Plugin**.
3. Choose the `mcp-adapter.zip` file → **Install Now** → **Activate**.

### What just happened (verify)

- The plugin created a default MCP server automatically.
- You can confirm the endpoint exists by opening this URL in your browser:
  ```
  https://your-site.com/wp-json/mcp/mcp-adapter-default-server
  ```
  A **`401` / "Unauthorized"** response is **correct** — it means the endpoint is alive and asking for a login. That's exactly what we want.

> **Note:** don't log in via the browser yet — we'll do it properly with the application password in a later step.

---

## Plugin 2 — Enable Abilities for MCP

**Source:** https://wordpress.org/plugins/enable-abilities-for-mcp/
**GitHub:** https://github.com/FabioMontenegro/enable-abilities-for-mcp

This plugin **requires MCP Adapter** to be active (you did that in step 1).

### Install

1. **Plugins → Add New**.
2. Search: **`Enable Abilities for MCP`**
3. The result is by **Fabio Montenegro**.
4. **Install Now** → **Activate**.

### Configure which abilities are exposed

1. In the left menu open **Settings → WP Abilities**.
2. On **first activation, all abilities are enabled.** You should **trim this down** to what the AI actually needs.
3. Recommended starting set (safe + useful):
   - ✅ All **Read** abilities (posts, pages, categories, tags, comments, media, users)
   - ✅ `create-post`, `update-post`, `upload-image`
   - ✅ Your SEO plugin's abilities (Rank Math / Yoast / AIOSEO / SEOPress — only the ones you use)
   - ✅ `clear-cache` (handy after edits)
   - ❌ **Turn OFF** anything you don't recognise
   - ❌ **Turn OFF** `delete-post`, `delete-cpt-item`, content translation, code snippets, user management — unless you specifically need them
4. Click **Save**.

> **Where the prefix comes from:** abilities bundled by this plugin appear as `ewpa/…` (e.g. `ewpa/get-posts`), WordPress core ones as `core/…`, and third-party ones as `<plugin-slug>/…`. You'll see these when connecting later.

---

## Plugin 3 — AI Office Hours (this kit)

**Download:** [`ai-office-hours.zip`](../ai-office-hours.zip) (in this repo)
**Source:** [`plugin/ai-office-hours/`](../plugin/ai-office-hours/)

### Install

1. Download `ai-office-hours.zip` from this repository.
2. WordPress admin → **Plugins → Add New → Upload Plugin**.
3. **Choose File** → select `ai-office-hours.zip` → **Install Now**.
4. Click **Activate**.

### First-run check

- A new menu appears: **Settings → AI Office Hours**.
- Until you create the AI user (next guide), the *Target user* dropdown will be empty — that's fine.
- Full configuration is in **[03 — AI Office Hours](03-ai-office-hours.md)**.

---

## Troubleshooting install

| Problem | Cause | Fix |
|---|---|---|
| "Plugin requires WordPress 6.9" | Old WordPress | Update WordPress (Dashboard → Updates) |
| MCP Adapter search shows nothing | Plugin directory not refreshed | Use the zip from the GitHub releases page |
| "Enable Abilities requires MCP Adapter" | Adapter not active | Activate MCP Adapter first, then retry |
| The endpoint URL gives `404` | Permalinks set to "Plain" | Settings → Permalinks → choose **Post name** → Save. REST routes need pretty permalinks. |
| "Application Passwords" section missing later | Site is HTTP (not HTTPS) or a security plugin hides it | Make sure the site is HTTPS; temporarily disable security plugins that block app passwords |

Continuing? → [02 — Create the AI user & application password](02-wordpress-ai-user.md)
