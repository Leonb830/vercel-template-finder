# Optional CLI route

Use an existing executable and populated index when available. For a one-off request, live web browsing is sufficient. If installation is requested or necessary for repeated catalog work, choose the runtime already used in the project; prefer a virtual environment for Python and avoid unsolicited global configuration changes.

```bash
pip install vercel-templates-discovery
# Alternative Node package:
npm install -g @imkxnny/vercel-templates-discovery
```

Check `vercel-templates --help` for the installed version. Commands observed in upstream Python source:

```bash
vercel-templates stats
vercel-templates search "portfolio" --limit 5 --json
vercel-templates recommend "next.js,tailwind" --limit 5 --json
vercel-templates show /templates/next.js/portfolio-starter-kit --json
vercel-templates diff /templates/next.js/chatbot /templates/next.js/nextjs-commerce --json
vercel-templates export --output templates.json
```

If the catalog is absent and the user wants a local index, run `vercel-templates index`. In the inspected revision, `index()` resets the database even without `--reset`; do not call it as a harmless readiness check. Preserve a useful existing catalog before a requested rebuild. Duration depends on network access and catalog size.

Keyword search needs no embedding service. Semantic search is optional and depends on the installed package and configured embedding provider. If unavailable, use keyword search or live browsing rather than installing additional engines automatically.

The Python revision inspected uses `~/.vercel_templates/templates.db` by default. Do not rely on the original skill's `VTD_DB_PATH` claim without checking the installed version. CLI and MCP records lack image/demo fields in that revision; enrich only the selected records with `create_carousel.py`.

An existing MCP integration may expose search, detail, category, recent, trending, and recommendation tools. Discover its schemas instead of assuming this reference is its API contract. REST/MCP server setup is optional and outside ordinary template discovery.
