# Vercel Template Finder

An agent skill for finding and comparing Vercel starter templates. It can search the live gallery without requiring the optional local catalog, explain each choice in plain language, and generate an accessible carousel with published template previews and demo links.

The carousel helper uses Python's standard library. It can fetch metadata for selected official Vercel template pages and writes a standalone HTML carousel plus a JSON manifest. It does not deploy templates or install project dependencies.

## Install with skills CLI

```bash
npx skills add Leonb830/vercel-template-finder --skill vercel-template-finder
```

The skill is located at `skills/vercel-template-finder/`.

## Generate a carousel

Prepare a UTF-8 JSON array of selected templates, each with an official Vercel template `detail_url`, then run:

```bash
python3 skills/vercel-template-finder/scripts/create_carousel.py \
  --input selected-templates.json \
  --output template-carousel.html \
  --title "Templates for your project" \
  --enrich
```

`--enrich` reads metadata from the selected Vercel detail pages to discover published preview images and demo links. Images load from their public hosts in the browser. See the skill's `SKILL.md` for input fields, workflow, and limitations.

## Based on

This skill builds on the open-source [Vercel Templates Discovery](https://github.com/imKXNNY/vercel-templates-discovery) project and its MIT-licensed skill. This repository adapts the workflow and adds a local preview-carousel generator; it is not affiliated with Vercel.
