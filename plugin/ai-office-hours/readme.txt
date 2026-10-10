=== AI Office Hours ===
Contributors: plumberqt
Tags: ai, mcp, security, roles, office hours
Requires at least: 6.0
Tested up to: 6.9
Requires PHP: 7.4
Stable tag: 1.0.0
License: GPLv2 or later
License URI: https://www.gnu.org/licenses/gpl-2.0.html

Time-boxed access for an AI agent user. Full-access role during office hours, read-only lock outside. Weekly off, holidays, manual Grant/Revoke.

== Description ==

Give your AI assistant the power to edit content during working hours — and automatically lock it to read-only outside them.

If an AI can edit your live site, you want two guarantees:

* It can only do what a limited role allows (an Editor, not an Administrator).
* It can only do it when you're around.

This plugin delivers the second. It forces the AI's WordPress user into a full-access role during office hours and a read-only role the rest of the time — automatically, on the server, on every request.

= Features =

* **Office-hours window** — e.g. 10:30 – 18:30, in your site timezone. Overnight windows supported.
* **Weekly off-day** — e.g. Wednesday, locked all day.
* **Holidays** — add specific dates for a full-day lock.
* **Instant lock** — outside the window the user becomes read-only.
* **Manual override** — Grant access now / Revoke access now / Resume auto schedule.
* **Capability checkboxes** — control what the "day" role can do.
* **One target user** — only the AI account is affected; never your admin.
* **Lightweight** — one file, no dependencies, no external calls.

= How it works =

The plugin creates two roles:

* `ai_day` — based on Editor, plus the extra capabilities you tick.
* `ai_night` — `read` only (read-only).

On every request, via the `determine_current_user` filter, it checks whether the target user's role matches the schedule and corrects it before WordPress checks capabilities. An hourly WP-Cron job keeps the database in sync as a backup.

Because the role is corrected per request, there is no way to hold elevated access past closing time.

= Roles created =

* AI Day (Office Hours) — `ai_day`
* AI Night (Locked) — `ai_night`

== Installation ==

1. Upload the plugin zip via Plugins > Add New > Upload Plugin, or install the folder into `/wp-content/plugins/`.
2. Activate the plugin through the Plugins screen.
3. Go to Settings > AI Office Hours.

== Frequently Asked Questions ==

= Does it touch my admin account? =

No. Only the single target user configured on the settings page.

= Can I use an overnight window? =

Yes. Set an end time earlier than the start time (e.g. 22:00 – 06:00).

= Are holidays respected in my timezone? =

Yes, the plugin uses the site timezone (Settings > General).

= What roles does it create? =

`ai_day` (based on Editor) and `ai_night` (read-only). You can point the day/night settings at any existing role if you prefer.

= How do I remove it completely? =

Set the target user back to a normal role, delete the plugin, then remove the `ai_day` and `ai_night` roles with a roles-management plugin if desired.

== Screenshots ==

1. Settings screen with status card, window, weekly off, target user, and capability checkboxes.

== Changelog ==

= 1.0.0 =
* Initial release.

== Upgrade Notice ==

= 1.0.0 =
Initial release.
