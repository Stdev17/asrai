# Web research: fetch ladder

Climb only as far as needed. Stop at the first rung that returns real content.

Rungs 2-4 are Firecrawl operations, named by REST endpoint against
`https://api.firecrawl.dev/v2`. MCP tools (`firecrawl_scrape`), CLI subcommands
(`firecrawl scrape`), and SDK methods (`firecrawl.scrape()`) all map onto these 1:1 —
use whichever binding the runtime exposes.

1. **Built-in fetch** — static HTML, public, single page. Free; use by default.
2. **`POST /scrape`** — JS-rendered shells, bot walls, PDFs (`parsers: ["pdf"]`),
   consent/geo walls (`location`), cross-host redirects.
   - `maxAge: 0` for anything time-sensitive (pricing, status, changelogs).
     Indexed content is reused by default, so a stale page returns as a fresh 200.
   - `proxy: "auto"` self-escalates. Don't hand-pick a tier.
   - `formats: ["summary"]` to triage many pages without filling context.
3. **`POST /map`**, then **`POST /crawl`** — need a whole section, not one page.
   Map first to enumerate URLs, then crawl with `includePaths` scoped to what matters.
4. **`POST /scrape/{scrapeId}/interact`** — content only exists after a click,
   scroll, or form submit.

Discovery when the URL is unknown: **`POST /search`**. Attaching `scrapeOptions` is the
cheap bulk path, but those fetches ignore `maxAge` — use it to find pages, then
re-scrape the few that carry the claim.

On failure, diagnose — never guess or retry with tweaked params:
**`POST /support/ask`** with the job ID in the question, which returns prose plus
machine-readable `fixParameters`. Where the CLI is installed, `firecrawl doctor <job-id>`.

## Unreachable — substitute immediately, do not retry

- **reddit.com** — policy-blocked at the API. Identical error on every proxy tier,
  stealth included; the request never leaves Firecrawl, so no proxy setting helps.
  `/.json`, `api.reddit.com`, and `old.reddit.com` all 403 from datacenter IPs.
  Substitute: `POST /search` with `site:reddit.com/r/<sub> <query>` and cite the
  result snippets. Full thread access requires Reddit OAuth credentials.
- **Hard paywalls** (WSJ, FT, Bloomberg), **SSO/auth-gated apps**, **PACER**.
  A 200 carrying only teaser text is not success — confirm body content before citing.

Verified 2026-09-13 against api.firecrawl.dev/v2.
