"""
Generate a detailed Word (.docx) guide: connecting an AI assistant to WordPress over MCP,
the AI Office Hours plugin, all required plugins with links, tiny steps, multi-site setup,
and troubleshooting.

Run:  python build_mcp_guide_docx.py
Out:  WordPress-AI-MCP-Setup-Guide.docx
"""

import docx
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.opc.constants import RELATIONSHIP_TYPE as RT

DOC = Document()

# ---------- base styles ----------
NORMAL = DOC.styles["Normal"]
NORMAL.font.name = "Calibri"
NORMAL.font.size = Pt(11)

for sec in DOC.sections:
    sec.left_margin = Inches(0.9)
    sec.right_margin = Inches(0.9)
    sec.top_margin = Inches(0.8)
    sec.bottom_margin = Inches(0.8)


def add_hyperlink(paragraph, url, text):
    part = paragraph.part
    r_id = part.relate_to(url, RT.HYPERLINK, is_external=True)
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), r_id)
    new_run = OxmlElement("w:r")
    rPr = OxmlElement("w:rPr")
    color = OxmlElement("w:color"); color.set(qn("w:val"), "0563C1")
    u = OxmlElement("w:u"); u.set(qn("w:val"), "single")
    rPr.append(color); rPr.append(u)
    new_run.append(rPr)
    t = OxmlElement("w:t"); t.text = text; new_run.append(t)
    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)


def H(text, level=1):
    DOC.add_heading(text, level=level)


def P(text="", bold=False, italic=False, size=None):
    p = DOC.add_paragraph()
    r = p.add_run(text)
    r.bold = bold
    r.italic = italic
    if size:
        r.font.size = Pt(size)
    return p


def bullet(text, bold_prefix=None):
    p = DOC.add_paragraph(style="List Bullet")
    if bold_prefix:
        r = p.add_run(bold_prefix); r.bold = True
        p.add_run(text)
    else:
        p.add_run(text)
    return p


def number(text):
    return DOC.add_paragraph(text, style="List Number")


def code(text):
    p = DOC.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.25)
    r = p.add_run(text)
    r.font.name = "Consolas"
    r.font.size = Pt(9.5)
    rPr = r._element.get_or_add_rPr()
    rFonts = OxmlElement("w:rFonts")
    rFonts.set(qn("w:ascii"), "Consolas")
    rFonts.set(qn("w:hAnsi"), "Consolas")
    rPr.append(rFonts)
    return p


def note(text):
    p = DOC.add_paragraph()
    r = p.add_run(text); r.italic = True
    r.font.color.rgb = RGBColor(0x99, 0x66, 0x00)
    return p


def table(headers, rows, widths=None):
    t = DOC.add_table(rows=1, cols=len(headers))
    t.style = "Light Grid Accent 1"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = t.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = ""
        run = hdr[i].paragraphs[0].add_run(h)
        run.bold = True
    for row in rows:
        cells = t.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = str(val)
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Inches(w)
    DOC.add_paragraph()
    return t


# =====================================================================
# TITLE
# =====================================================================
title = DOC.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = title.add_run("WordPress + AI over MCP")
r.bold = True; r.font.size = Pt(28); r.font.color.rgb = RGBColor(0x21, 0x75, 0x9B)

sub = DOC.add_paragraph()
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = sub.add_run("Complete Setup Guide — building the connection, all required plugins, the AI Office Hours plugin, and connecting multiple websites")
r.italic = True; r.font.size = Pt(12)

sub2 = DOC.add_paragraph()
sub2.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = sub2.add_run("Repo: "); r.font.size = Pt(10)
add_hyperlink(sub2, "https://github.com/plumberqt/wordpress-ai-mcp-kit", "github.com/plumberqt/wordpress-ai-mcp-kit")

DOC.add_paragraph()

# =====================================================================
# 1. OVERVIEW
# =====================================================================
H("1. What this is and why", 1)
P("This guide shows how to connect an AI assistant (opencode, Claude, Cursor, VS Code — any MCP "
  "client) to a live WordPress site so it can manage content: create drafts, edit posts, fix SEO "
  "meta, upload images, moderate comments.")
P("The whole point is SAFETY. Instead of giving the AI your admin password, you:")
bullet("give it a normal, low-privilege WordPress account (an Editor, never an Administrator);", bold_prefix="Least privilege — ")
bullet("let it write only during your working hours, automatically locking it to read-only afterwards;", bold_prefix="Least time — ")
bullet("expose only the actions (abilities) you explicitly switch on;", bold_prefix="Least ability — ")
bullet("approve every single action in your AI client.", bold_prefix="Human in the loop — ")
P()
P("Three independent safety layers mean you would have to defeat all of them at once to do damage. "
  "By design, the AI can NEVER touch theme files, plugin files, .htaccess, wp-config.php, users, "
  "roles, settings, or plugins.")

# =====================================================================
# 2. COMPONENTS / PLUGINS
# =====================================================================
H("2. Components — every plugin & tool, with links", 1)
P("You need three WordPress plugins, one local proxy program, and one AI client. All are free.")

H("2.1 MCP Adapter  (official WordPress plugin)", 2)
P("What it does: bridges the WordPress Abilities API to MCP and creates the server endpoint your AI connects to.")
bullet("Plugin directory: wordpress.org/plugins/mcp-adapter/")
bullet("GitHub: github.com/WordPress/mcp-adapter")
bullet("Direct zip (latest): github.com/WordPress/mcp-adapter/releases/latest/download/mcp-adapter.zip")
bullet("Requires: WordPress 6.9+, PHP 7.4+")
p = DOC.add_paragraph(); r = p.add_run("Links: "); r.bold = True
add_hyperlink(p, "https://wordpress.org/plugins/mcp-adapter/", "wordpress.org/plugins/mcp-adapter"); p.add_run("  |  ")
add_hyperlink(p, "https://github.com/WordPress/mcp-adapter", "github.com/WordPress/mcp-adapter")

H("2.2 Enable Abilities for MCP  (by Fabio Montenegro)", 2)
P("What it does: registers about 102 ready-made abilities — posts, pages, categories, tags, comments, "
  "media, users, menus, SEO (Rank Math / Yoast / AIOSEO / SEOPress), WooCommerce, JetEngine, cache "
  "purge, llms.txt — and gives you a dashboard (Settings > WP Abilities) to toggle each one on/off, "
  "plus an activity log.")
bullet("Plugin directory: wordpress.org/plugins/enable-abilities-for-mcp/")
bullet("GitHub: github.com/FabioMontenegro/enable-abilities-for-mcp")
bullet("Requires: WordPress 6.9+, PHP 8.0+, and MCP Adapter active")
p = DOC.add_paragraph(); r = p.add_run("Links: "); r.bold = True
add_hyperlink(p, "https://wordpress.org/plugins/enable-abilities-for-mcp/", "wordpress.org/plugins/enable-abilities-for-mcp"); p.add_run("  |  ")
add_hyperlink(p, "https://github.com/FabioMontenegro/enable-abilities-for-mcp", "github.com/FabioMontenegro/enable-abilities-for-mcp")

H("2.3 AI Office Hours  (this kit — ours)", 2)
P("What it does: forces the AI's WordPress user into a full-access role during your office hours and "
  "a read-only role outside them. Weekly off-day, holidays, and Grant / Revoke / Resume buttons.")
bullet("Download: the ai-office-hours.zip in this repo")
bullet("Guide: docs/03-ai-office-hours.md")
bullet("Requires: WordPress 6.0+, PHP 7.4+")
p = DOC.add_paragraph(); r = p.add_run("Link: "); r.bold = True
add_hyperlink(p, "https://github.com/plumberqt/wordpress-ai-mcp-kit", "github.com/plumberqt/wordpress-ai-mcp-kit")

H("2.4 @automattic/mcp-wordpress-remote  (local proxy)", 2)
P("What it does: a small program that translates between your AI client (STDIO) and WordPress (HTTP), "
  "and injects the credentials. You never install it globally — npx fetches it on demand.")
bullet("npm: npmjs.com/package/@automattic/mcp-wordpress-remote")
bullet("GitHub: github.com/Automattic/mcp-wordpress-remote")
bullet("Requires: Node.js 18+")
p = DOC.add_paragraph(); r = p.add_run("Links: "); r.bold = True
add_hyperlink(p, "https://www.npmjs.com/package/@automattic/mcp-wordpress-remote", "npmjs.com/package/@automattic/mcp-wordpress-remote"); p.add_run("  |  ")
add_hyperlink(p, "https://github.com/Automattic/mcp-wordpress-remote", "github.com/Automattic/mcp-wordpress-remote")

H("2.5 opencode  (the AI client)", 2)
P("What it does: the command-line AI coding assistant used in this guide. It reads the config, "
  "connects the MCP server, and asks you before each action.")
bullet("Website: opencode.ai")
bullet("Install: npm i -g opencode-ai")
bullet("Requires: Node.js 18+")
p = DOC.add_paragraph(); r = p.add_run("Link: "); r.bold = True
add_hyperlink(p, "https://opencode.ai", "opencode.ai")

P()
P("Any MCP client works — Claude Desktop, Cursor, VS Code Copilot, Windsurf. Just point them at the "
  "same endpoint with the same application password.", bold=True)

# =====================================================================
# 3. HOW IT WORKS
# =====================================================================
H("3. How the connection works", 1)
P("The chain, in plain language:")
number("WordPress 6.9+ ships the Abilities API — a standard menu of things a site can do.")
number("The official MCP Adapter plugin turns those abilities into MCP tools and serves them at a REST endpoint: https://YOUR-SITE.com/wp-json/mcp/mcp-adapter-default-server")
number("Enable Abilities for MCP registers the useful abilities and lets you toggle each one.")
number("AI Office Hours forces the AI's user into the correct role based on the clock (full access in hours, read-only outside).")
number("Your AI client talks to the endpoint through the mcp-wordpress-remote proxy using an Application Password.")
number("opencode's permission rules make it prompt you before every WordPress action.")

P()
P("One request, end to end:")
code("you -> opencode -> (permission prompt) -> mcp-wordpress-remote -> HTTPS")
code("     -> WordPress: determine_current_user -> AI Office Hours sets role")
code("     -> ability capability check -> draft created -> JSON back to you")

P()
P("The AI client only ever calls THREE meta-tools, then discovers the rest:")
bullet("mcp-adapter/discover-abilities — what can you do?")
bullet("mcp-adapter/get-ability-info — how do I use this one?")
bullet("mcp-adapter/execute-ability — run this one with these inputs")

# =====================================================================
# 4. SETUP
# =====================================================================
H("4. The complete setup — every tiny step", 1)
note("Do the steps in order. Do not skip ahead — each step depends on the previous one.")

H("Step 0 — Check your versions", 2)
P("In WordPress admin: Dashboard > At a Glance, or Tools > Site Health > Info > Server.")
bullet("WordPress must be 6.9 or newer (update first if not).")
bullet("PHP 8.0+ recommended (7.4 minimum).")
bullet("On your computer install Node.js 18+ from nodejs.org.")

H("Step 1 — Install MCP Adapter", 2)
number("WordPress admin > Plugins > Add New.")
number("Search: MCP Adapter.")
number("Pick the result by 'WordPress.org Contributors' (watch the author — avoid copycats).")
number("Install Now, then Activate.")
P("If search fails, upload the zip from GitHub Releases:")
code("https://github.com/WordPress/mcp-adapter/releases/latest/download/mcp-adapter.zip")
P("Verify: open https://YOUR-SITE.com/wp-json/mcp/mcp-adapter-default-server — a 401/Unauthorized "
  "response is CORRECT (the endpoint exists and wants a login).")

H("Step 2 — Install Enable Abilities for MCP", 2)
number("Plugins > Add New > search: Enable Abilities for MCP.")
number("Pick the one by Fabio Montenegro. Install Now, Activate.")
number("Go to Settings > WP Abilities and trim the list to what you need.")
P("Recommended starting set:")
bullet("ON: all Read abilities, create-post, update-post, upload-image, your SEO plugin's abilities, clear-cache.")
bullet("OFF: anything you don't recognise, delete-post, code snippets, user/role management, translation.")

H("Step 3 — Create the AI user", 2)
number("Users > Add New.")
number("Username: ai-agent  (keep this exact name).")
number("Email: any address you control (e.g. ai-agent@your-site.com).")
number("Password: save it somewhere, but the AI uses an Application Password instead.")
number("Role: Editor  (NOT Administrator).")
number("Add New User.")
P("Why Editor? An Editor can manage posts, pages, media, and comments, but cannot touch plugins, "
  "themes, users, or settings.")

H("Step 4 — Create the Application Password", 2)
number("Users > click ai-agent to edit its profile.")
number("Scroll to the bottom: the 'Application Passwords' section.")
number("Name it: opencode.")
number("Click Add New Application Password.")
number("Copy the password shown (xxxx xxxx xxxx xxxx) — it is shown ONLY ONCE.")
note("If you don't see the Application Passwords section: the site must be HTTPS, and a security "
     "plugin may be hiding it. See the troubleshooting section.")

H("Step 5 — Store the password as an environment variable (Windows)", 2)
P("Open PowerShell and run (paste your real password):")
code('setx WP_APP_PASSWORD "xxxx xxxx xxxx xxxx"')
bullet("setx saves it permanently for your Windows user account.")
bullet("New processes only — any app already open (VS Code, terminal) won't see it until you restart that app.")
P("Verify in a NEW terminal:")
code('[Environment]::GetEnvironmentVariable("WP_APP_PASSWORD","User")')
P("macOS/Linux: add export WP_APP_PASSWORD=\"xxxx xxxx xxxx xxxx\" to ~/.zshrc or ~/.bashrc, then reload.")

H("Step 6 — Install the AI Office Hours plugin", 2)
number("Download ai-office-hours.zip from the repo.")
number("Plugins > Add New > Upload Plugin > Choose File > Install Now > Activate.")
number("Open Settings > AI Office Hours.")

H("Step 7 — Configure AI Office Hours", 2)
table(
    ["Setting", "Value to use"],
    [
        ["Auto switch", "ON (leave the schedule in charge)"],
        ["Office window", "10:30 – 18:30 (adjust to your day)"],
        ["Weekly off day", "Wednesday (or your choice)"],
        ["Target user", "ai-agent"],
        ["Day role / Night role", "ai_day / ai_night (defaults)"],
        ["Extra powers", "Only 'Styling & Menus' unless you need more"],
        ["Holidays", "Add dates as they come"],
    ],
    widths=[2.0, 4.5],
)
P("Check Settings > General > Timezone is correct (e.g. Asia/Kolkata). The status card should read "
  "'FULL ACCESS (office hours)' during the window.")

H("Step 8 — Set up opencode", 2)
number("Install: opencode (npm i -g opencode-ai) and Node.js 18+.")
number("In your project folder create .opencode/opencode.json (copy from examples/opencode.json).")
number("Edit only WP_API_URL (your endpoint) and keep WP_API_USERNAME as ai-agent.")
number("Leave WP_API_PASSWORD as {env:WP_APP_PASSWORD} — it reads the OS variable. Never paste the real password in the file.")
P("The config also adds safety prompts:")
code('"permission": { "wordpress_*": "ask", "bash": { "*": "ask", "rm *": "deny" } }')

H("Step 9 — Add the AI rules file (AGENTS.md)", 2)
P("Create .opencode/AGENTS.md (copy from examples/AGENTS.md). It tells the AI: always create drafts, "
  "never publish without approval, never delete, and stop on 'forbidden'.")

H("Step 10 — Restart and test", 2)
number("Fully close your editor (VS Code: all windows) and terminal — so the new env var is visible.")
number("Open a new terminal, cd to the project, run: opencode mcp list.")
P("You should see:")
code("wordpress  ✓ connected")
number("Start opencode and say: 'List recent posts from WordPress.'")
number("A permission prompt appears — choose Allow always (reads) or Allow once.")
number("Test a write: 'Create a test draft post titled MCP Test.' Choose Allow once.")
number("Delete the test draft when done.")
number("Test the lock: click Revoke access now in AI Office Hours, try creating a draft again — it should return forbidden. Click Resume auto schedule.")

# =====================================================================
# 5. MULTIPLE WEBSITES
# =====================================================================
H("5. Connecting multiple websites", 1)
P("The same kit works for many sites. Only the endpoint URL and the credentials differ per site.")

H("5.1 Recommended: one project per site", 2)
P("Give each site its own project folder with its own .opencode/opencode.json:")
code("D:\\work\\site-a\\.opencode\\opencode.json   -> WP_APP_PASSWORD_A")
code("D:\\work\\site-b\\.opencode\\opencode.json   -> WP_APP_PASSWORD_B")
P("Run opencode inside the site's folder and it only ever sees that site — impossible to edit the wrong one.")

H("5.2 Steps for each new site", 2)
number("On the new site: install MCP Adapter + Enable Abilities for MCP.")
number("Create ai-agent (Editor) and an Application Password.")
number("Install & configure ai-office-hours.zip.")
number("Save the new password under a NEW variable: setx WP_APP_PASSWORD_SITE_B \"....\"")
number("In the new project config set WP_API_URL to site B's endpoint and WP_API_PASSWORD to {env:WP_APP_PASSWORD_SITE_B}.")
number("Restart the editor; run opencode mcp list; confirm it connects.")

H("5.3 Advanced: two sites in ONE project", 2)
P("Define two MCP servers with different names:")
code('"mcp": {')
code('  "wordpress_a": { ... WP_API_URL: site-a ... , WP_API_PASSWORD: {env:WP_APP_PASSWORD_A} },')
code('  "wordpress_b": { ... WP_API_URL: site-b ... , WP_API_PASSWORD: {env:WP_APP_PASSWORD_B} }')
code('}')
P("Then in permissions:")
code('"permission": { "wordpress_a_*": "ask", "wordpress_b_*": "ask" }')
bullet("Server names become tool prefixes (wordpress_a_..., wordpress_b_...).")
bullet("Tell the AI explicitly which site each time, and prefer one-project-per-site for client work.")

H("5.4 Other AI clients", 2)
table(
    ["Client", "Where the config goes"],
    [
        ["opencode", ".opencode/opencode.json"],
        ["Claude Desktop", "claude_desktop_config.json > mcpServers.wordpress"],
        ["Claude Code", "claude mcp add / .mcp.json"],
        ["Cursor", "Settings > MCP"],
        ["VS Code (Copilot)", ".vscode/mcp.json"],
    ],
    widths=[2.0, 4.5],
)
P("All use the same proxy command and the same three env values.")

# =====================================================================
# 6. TROUBLESHOOTING
# =====================================================================
H("6. Troubleshooting — every error and its fix", 1)
table(
    ["Symptom", "Cause", "Fix"],
    [
        ["mcp list shows 'error'", "Proxy won't start / Node missing", "Run 'node -v' (need 18+); run npx -y @automattic/mcp-wordpress-remote manually to see the error"],
        ["Every call -> 401", "Password wrong or env var not visible", "Restart editor; recheck the var in a new terminal; verify username/URL"],
        ["Every call -> 403", "Security plugin or host blocks Basic auth", "Deactivate security plugin, whitelist ai-agent; or add SetEnvIf Authorization rule"],
        ["Endpoint URL -> 404", "Permalinks are 'Plain'", "Settings > Permalinks -> Post name -> Save"],
        ["No abilities found", "Enable Abilities for MCP inactive or all toggled off", "Activate it; enable abilities in Settings > WP Abilities"],
        ["'invalid input' errors", "Value fails the ability schema (e.g. order 'desc')", "Call get-ability-info for exact allowed values; retry with correct casing"],
        ["AI still writes after hours", "Wrong timezone / target user / override", "Fix Settings > General timezone; set target user; click Resume auto schedule"],
        ["Can't write during hours", "ai_night assigned or extra unchecked", "Resume auto schedule; re-tick needed extras; Save"],
        ["Application Passwords section missing", "Site not HTTPS, or security plugin hides it", "Enable HTTPS; temporarily disable security plugins"],
        ["Zip: 'No valid plugins found'", "Wrong zip structure", "Use the ai-office-hours.zip from this repo (folder/ai-office-hours.php)"],
    ],
    widths=[1.9, 2.1, 2.5],
)

# =====================================================================
# 7. SECURITY
# =====================================================================
H("7. Security checklist", 1)
for item in [
    "AI uses a separate ai-agent account with role Editor (never admin).",
    "Application Password stored in an OS env var (WP_APP_PASSWORD), never in a file.",
    "DISALLOW_FILE_EDIT is true in wp-config.php.",
    "AI Office Hours: auto ON, correct timezone, target user set, weekly off + holidays set.",
    "Settings > WP Abilities: only needed abilities enabled; delete/user/code abilities OFF.",
    "opencode permission: 'wordpress_*': 'ask' present.",
    "You know the three revoke switches (Revoke button, window close, delete app password).",
]:
    p = DOC.add_paragraph(item, style="List Bullet")
    p.runs[0].text = "[ ] " + item

P()
P("Harden wp-config.php (add above the 'stop editing' line; back up first):")
code("define( 'DISALLOW_FILE_EDIT', true );")
code("define( 'DISALLOW_FILE_MODS', true );   // optional")

# =====================================================================
# 8. FAQ
# =====================================================================
H("8. FAQ", 1)
faqs = [
    ("Do I need to expose my site publicly?",
     "It already is — this is the same HTTPS REST API WordPress uses for apps. No SSH, no FTP, no extra port."),
    ("Is the password safe in plain text?",
     "It is never in a file. It lives in an OS environment variable and the config references it as {env:WP_APP_PASSWORD}."),
    ("Can I revoke access instantly?",
     "Yes — click Revoke in AI Office Hours, or let the window close, or delete the Application Password. All apply on the next request."),
    ("Which SEO plugins are supported?",
     "Rank Math, Yoast SEO, All in One SEO (AIOSEO), and SEOPress — whichever you have active."),
    ("Will it work on shared hosting?",
     "Yes, as long as WordPress is 6.9+ and PHP is 7.4+ (8.0+ recommended)."),
    ("Does it work with multiple sites?",
     "Yes — see section 5."),
]
for q, a in faqs:
    p = DOC.add_paragraph(); r = p.add_run("Q: " + q); r.bold = True
    P("A: " + a)

# =====================================================================
# footer
# =====================================================================
DOC.add_paragraph()
foot = DOC.add_paragraph()
foot.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = foot.add_run("Built by plumberqt  ·  ") ; r.italic = True; r.font.size = Pt(9)
add_hyperlink(foot, "https://github.com/plumberqt/wordpress-ai-mcp-kit", "wordpress-ai-mcp-kit")
r2 = foot.add_run("  ·  GPL-2.0-or-later"); r2.italic = True; r2.font.size = Pt(9)

OUT = "WordPress-AI-MCP-Setup-Guide.docx"
DOC.save(OUT)
print("Wrote", OUT)
