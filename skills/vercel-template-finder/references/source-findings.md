# Source findings and local design

Inspected on 2026-10-16: [imKXNNY/vercel-templates-discovery](https://github.com/imKXNNY/vercel-templates-discovery), commit `b97794c5609147ebea51986f92b575c1b5c4e2b3`. The REA skill routes complete source repositories through normal source inspection; no binary decompilation or REA MCP setup was needed.

## Observed in source

- `vercel_templates/scraper.py`, `discover_templates()` and `enrich_template()`: scrape gallery categories and detail HTML/RSC data into metadata records. No public catalog API is used by this implementation.
- `vercel_templates/scraper.py`, `_init_db()`, and `ts/src/db.ts`, `init()`: SQLite records include title, description, taxonomy, repository, README, install command, detail URL, and index time. They have no image or live-demo fields.
- `vercel_templates/scraper.py`, `index()`: unconditionally calls `reset_db()` before crawling. The original instructions overstate the safety of routine indexing.
- `vercel_templates/config.py`, `cache_db_path()`: computes `~/.vercel_templates/templates.db`; the original skill's environment-variable default is not supported here.
- `catalog.json`: some records contain `git clone https://github.com/.../tree/...`, which is not a usable Git remote command. Inspect repository setup before scaffolding.
- Original `SKILL.md`: requires installation/indexing and excludes visual browsing. Its example search result contains no preview image.

## Observed on the public template page

The [Next.js Boilerplate detail page](https://vercel.com/templates/next.js/nextjs-boilerplate) served a deployment link with `demo-image`, `demo-url`, and `repository-url` query parameters, plus an `og:image` social preview. These are published metadata, not observations of the demo executing. The layout or fields can change, so extraction has explicit missing/error results.

## Local design choices

- Use the existing CLI/MCP when useful and allow live browsing without setup.
- Keep the upstream engine untouched; add a standard-library helper inside the installed skill.
- Enrich only chosen pages, retain image provenance, and render a standalone accessible HTML carousel with a JSON manifest.
- Use published demo images first and label social-image fallbacks. Missing or broken images remain explicit.
- No deployment, dependency installation, or MCP registration occurs during carousel generation.

This is a local skill enhancement, not an upstream repository release. Static source inspection establishes the architecture above; it does not validate every CLI, API, embedding provider, or catalog record.
