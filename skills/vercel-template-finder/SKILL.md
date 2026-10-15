---
name: vercel-template-finder
description: Find and compare Vercel starter templates for a project, explain the tradeoffs in plain language, and show the selected templates in a visual carousel with real preview images and demo links. Use for template discovery, visual browsing, or choosing a starter; not general deployment support.
metadata:
  version: "2.0.0-local"
  upstream: "https://github.com/imKXNNY/vercel-templates-discovery"
---

# Vercel Template Finder

Help the user choose a starter they can understand and use. Accept ordinary requests such as “find a clean portfolio” or “show me three shop templates.” Infer useful search terms from their project; ask only when a missing constraint would materially change the shortlist. Explain unfamiliar stack names briefly when they affect the choice.

## Find a useful shortlist

Use an available discovery route:

- **No setup needed:** search the web with `site:vercel.com/templates` plus the user's project and stack, or browse the relevant Vercel gallery category. Open the candidate detail pages to verify claims. This is a live browsing fallback; it is not a CLI search.
- **Existing CLI or MCP:** reuse a populated local catalog. Check `vercel-templates stats` if index status is unknown, then search or recommend. Use the connected MCP server's actual schemas. See [CLI reference](references/cli.md) for commands and setup when needed.
- **Unavailable catalog or tools:** continue with live browsing. Do not make installing a package, Ollama, Docker, or an MCP server a prerequisite for an ordinary recommendation.

Usually shortlist 3–5 distinct candidates, or honor the user's count. Verify the chosen templates on their official detail pages and, when needed, their linked repositories. Filter for explicit requirements before judging appearance. Avoid claiming an exhaustive search. A cached catalog is a source of candidates, not proof of current availability.

For each choice, explain its best use, why it fits, and the main setup cost or limitation. Distinguish documented features from your assessment. Do not invent compatibility, pricing, licenses, maintenance status, or numerical fit scores. Mark a top pick only when the user's criteria support it.

## Show the choices visually

For a multi-template shortlist, create the carousel by default unless the user prefers text only. For one result, the same helper produces one card. Use actual template previews, never generated mockups presented as screenshots.

1. Write a UTF-8 JSON array of selected records to the task's work directory. Preserve the requested order. Required: `detail_url` (an official Vercel template detail URL). Useful fields: `title`, `description`, `reason`, `tradeoff`, `tags` (array of strings), and `recommended` (boolean). Optional verified fields: `github_url`, `demo_url`, `image_url`, `image_kind`, `image_source_url`. CLI records with `slug` also work.
2. Run the bundled helper with an absolute script path, substituting this skill's real directory and the task's output paths:

   ```bash
   python3 <skill-dir>/scripts/create_carousel.py \
     --input <work-dir>/selected-templates.json \
     --output <outputs-dir>/template-carousel.html \
     --title "Templates for your project" --enrich
   ```

   Python 3.10+ and its standard library are sufficient. `--enrich` reads only the selected Vercel pages. It extracts published demo images and demo/repository links from deployment metadata, then falls back to a labeled social preview. It writes the HTML and a companion `.json` manifest with sources, timestamps, and any errors. It does not install or deploy templates.
3. Inspect the returned manifest. If a selected page fails or has no image, use available browser tools to inspect that exact page or its verified public demo. A real browser screenshot can be supplied as an `image_url` relative to the output HTML, with `image_kind: "Demo screenshot"` and its source URL. Re-render without `--enrich` to preserve inspected data. Do not bypass a host's media restrictions by downloading blocked images. If no supported preview is available, retain the card with its explicit unavailable state and working source link.
4. Open the HTML in the available browser/panel and give the user a clickable output link. The carousel supports buttons, arrow/Home/End keys, touch scrolling, a live position indicator, reduced motion, and image-error fallbacks. Keep a brief text recommendation alongside it so the choice is understandable without images.

The generated file references public remote images, so they require internet access. A social preview is labeled as such; it is not a verified live screenshot. Image metadata retrieval does not establish that an image rendered: inspect the browser when claiming that previews work.

Do not promise a native inline chat carousel. Use an inline rendering tool only if it supports the actual image origins and interactions. Otherwise open the standalone HTML; if HTML cannot be shown, provide a Markdown list with supported image embeds and source links. Never emit unsupported carousel markup.

## Continue after selection

Return the verified template page, live demo, and repository when available. Scaffold or deploy only when the user's request includes that action. Read the selected repository's setup instructions before choosing an install command: a GitHub `/tree/...` URL cannot be used directly as a `git clone` URL. Preserve the user's framework and design constraints when moving into implementation.

For the original architecture, evidence, and limitations of this local revision, see [source findings](references/source-findings.md).
