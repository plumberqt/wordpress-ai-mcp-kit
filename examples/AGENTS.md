# WordPress rules

Connected via the `wordpress` MCP (an `ai-agent` user, office hours only, editor-level role).

## Hard rules — never break these

1. **Never delete** any post, page, category, tag, media, or menu item. If asked to "remove", unpublish or draft it instead.
2. **Never publish directly.** Always create/update as `draft` first, show me a summary, and wait for my explicit "publish" approval.
3. **Never touch:** theme files, plugin files, `.htaccess`, `wp-config.php`, users, roles, site settings, or plugins. (You have no capability for these anyway — don't attempt them.)
4. **Never install or activate** anything.
5. **Never change** the site URL, timezone, or permalinks.

## How to work

- New content → create as **draft**, then report what changed.
- Edits to existing posts → after editing, always report: post title + which sections changed.
- SEO meta (Rank Math / Yoast / AIOSEO / SEOPress) → update only the fields I explicitly mention.
- If any tool returns `forbidden`: office hours have ended or the role is locked. **Stop. Do not retry.** Tell me to click "Grant access now" in Settings → AI Office Hours.

## Responsive / device checks

Before saying any layout or CSS change is done, state which breakpoints were considered:

- Mobile: 360–414 px
- Tablet: 768–834 px
- Laptop: 1280–1440 px
- Desktop: 1920 px+

Test at these widths if a browser tool is available; otherwise say "not visually verified".
