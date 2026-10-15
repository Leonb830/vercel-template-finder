#!/usr/bin/env python3
"""Render selected Vercel templates; optionally read their public preview metadata."""

import argparse
import html
import json
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


def public_url(value):
    value = str(value or "").strip()
    if value.startswith("//"):
        value = "https:" + value
    try:
        parts = urlsplit(value)
        if parts.scheme not in ("https", "http") or not parts.hostname:
            return ""
        if parts.username or parts.password or any(c.isspace() for c in value):
            return ""
    except ValueError:
        return ""
    return value


def template_url(value):
    value = str(value or "").strip()
    if value.startswith(("/templates/", "templates/")):
        value = urljoin("https://vercel.com/", value)
    valid = public_url(value)
    parts = urlsplit(valid)
    if (parts.scheme != "https" or parts.hostname != "vercel.com"
            or parts.port not in (None, 443)
            or not parts.path.startswith("/templates/")
            or len(parts.path.strip("/").split("/")) < 3):
        raise ValueError(f"Expected an official Vercel template detail URL: {value!r}")
    return valid


class VercelRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        template_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class PageMetadata(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta = {}
        self.deploy = {}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "meta":
            key = attrs.get("property") or attrs.get("name")
            if key and attrs.get("content"):
                self.meta.setdefault(key.lower(), attrs["content"])
        if tag == "a" and attrs.get("href"):
            link = urlsplit(urljoin("https://vercel.com", attrs["href"]))
            if link.hostname == "vercel.com" and link.path == "/new/clone":
                params = parse_qs(link.query)
                for key in ("demo-image", "demo-url", "repository-url", "demo-title"):
                    if params.get(key):
                        self.deploy.setdefault(key, params[key][0])


def enrich(record):
    result = dict(record)
    url = template_url(result.get("detail_url") or result.get("slug"))
    result["detail_url"] = url
    result["checked_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    result.pop("fetch_error", None)
    try:
        request = Request(url, headers={"User-Agent": "VercelTemplatePreview/2.0", "Accept": "text/html"})
        with build_opener(VercelRedirect()).open(request, timeout=25) as response:
            if response.headers.get_content_type() != "text/html":
                raise ValueError("Template page did not return HTML")
            raw = response.read(5_000_001)
            if len(raw) > 5_000_000:
                raise ValueError("Template page exceeds 5 MB metadata limit")
            parser = PageMetadata()
            parser.feed(raw.decode(response.headers.get_content_charset() or "utf-8", errors="replace"))
        result["title"] = parser.deploy.get("demo-title") or parser.meta.get("og:title") or result.get("title")
        result["description"] = parser.meta.get("og:description") or result.get("description", "")
        for source, target in (("demo-url", "demo_url"), ("repository-url", "github_url")):
            link = public_url(parser.deploy.get(source))
            if link:
                result[target] = link
        # Explicit supplied screenshots survive enrichment; otherwise prefer published demo art.
        if not result.get("image_url"):
            demo_image = parser.deploy.get("demo-image")
            social_image = parser.meta.get("og:image") or parser.meta.get("twitter:image")
            for image, kind in ((demo_image, "Published demo image"), (social_image, "Social preview")):
                if image and public_url(urljoin(url, image)):
                    result.update(image_url=urljoin(url, image), image_kind=kind, image_source_url=url)
                    break
        result["metadata_status"] = "fetched"
    except (HTTPError, URLError, OSError, ValueError) as exc:
        result["metadata_status"] = "unavailable"
        result["fetch_error"] = str(exc)
    return result


def esc(value):
    return html.escape(str(value or ""), quote=True)


def image_url(value):
    """Allow public images or portable, relative screenshot files; never script/data URLs."""
    value = str(value or "").strip()
    remote = public_url(value)
    if remote:
        return remote
    parts = urlsplit(value)
    if (value and not parts.scheme and not parts.netloc and not value.startswith(("/", "\\"))
            and "\\" not in value and not any(c.isspace() for c in value)):
        return value
    return ""


def render_card(record, index, total):
    title = record.get("title") or record["detail_url"].rstrip("/").rsplit("/", 1)[-1].replace("-", " ")
    preview = image_url(record.get("image_url"))
    image = (f'<img src="{esc(preview)}" alt="Preview of {esc(title)}" '
             f'loading="{"eager" if index == 0 else "lazy"}" decoding="async" referrerpolicy="no-referrer">') if preview else ""
    source = public_url(record.get("image_source_url"))
    kind = record.get("image_kind") or "Provided preview"
    caption = (f'<a href="{esc(source)}" target="_blank" rel="noopener noreferrer">{esc(kind)}</a>'
               if source else esc(kind)) if preview else "Preview unavailable"
    tags = record.get("tags", [])
    if not tags:
        tags = [t.strip() for t in str(record.get("frameworks") or record.get("framework") or "").split(",") if t.strip()]
    if not isinstance(tags, list):
        tags = [str(tags)]
    tag_html = "".join(f'<span class="tag">{esc(tag)}</span>' for tag in tags[:6])
    badge = '<span class="pick">Recommended</span>' if record.get("recommended") is True else ""
    reasons = "".join(f'<div><dt>{label}</dt><dd>{esc(record[key])}</dd></div>'
                      for key, label in (("reason", "Why it fits"), ("tradeoff", "Consider")) if record.get(key))
    links = []
    for field, label in (("detail_url", "Template details"), ("demo_url", "Live demo"), ("github_url", "Source code")):
        link = public_url(record.get(field))
        if link:
            links.append(f'<a class="action" href="{esc(link)}" target="_blank" rel="noopener noreferrer">{label} <span aria-hidden="true">↗</span></a>')
    error = '<p class="notice">Page metadata could not be refreshed. Check the template details.</p>' if record.get("fetch_error") else ""
    return f'''<article class="slide" role="group" aria-roledescription="slide" aria-label="{index + 1} of {total}: {esc(title)}">
      <figure><div class="preview">{image}<div class="missing" {"hidden" if preview else ""}><span aria-hidden="true">▧</span>Preview unavailable</div></div><figcaption>{caption}</figcaption></figure>
      <div class="body"><div class="eyebrow"><span>OPTION {index + 1:02d}</span>{badge}</div>
      <h2>{esc(title)}</h2><p class="description">{esc(record.get("description"))}</p>
      <div class="tags">{tag_html}</div><dl>{reasons}</dl>{error}<nav class="links" aria-label="Links for {esc(title)}">{"".join(links)}</nav></div></article>'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="JSON array or object with templates array")
    parser.add_argument("--output", required=True, type=Path, help="Destination .html file")
    parser.add_argument("--title", default="Find your starting point")
    parser.add_argument("--enrich", action="store_true", help="Fetch selected public Vercel detail pages")
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
        records = data.get("templates") if isinstance(data, dict) else data
        if not isinstance(records, list) or not 1 <= len(records) <= 20:
            raise ValueError("Input must contain between 1 and 20 selected templates")
        if args.output.suffix.lower() != ".html":
            raise ValueError("Output must end with .html")
        for record in records:
            if not isinstance(record, dict):
                raise ValueError("Every template must be an object")
            record["detail_url"] = template_url(record.get("detail_url") or record.get("slug"))
        if args.enrich:
            records = [enrich(record) for record in records]
        for record in records:
            record["image_url"] = image_url(record.get("image_url"))
            record["preview_status"] = "available_url" if record["image_url"] else "unavailable"
        template = (Path(__file__).resolve().parent.parent / "assets" / "carousel.html").read_text(encoding="utf-8")
        # One pass prevents placeholder-like text in user content from being substituted.
        import re
        substitutions = {"TITLE": esc(args.title), "CARDS": "\n".join(render_card(r, i, len(records)) for i, r in enumerate(records)), "COUNT": str(len(records))}
        output = re.sub(r"\{\{(TITLE|CARDS|COUNT)\}\}", lambda m: substitutions[m[1]], template)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
        manifest = args.output.with_suffix(".json")
        manifest.write_text(json.dumps({"title": args.title, "templates": records}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps({"html": str(args.output.resolve()), "manifest": str(manifest.resolve()), "templates": len(records), "preview_urls": sum(bool(r["image_url"]) for r in records), "metadata_errors": sum(bool(r.get("fetch_error")) for r in records)}))
    except (OSError, ValueError, TypeError) as exc:
        parser.exit(1, f"Error: {exc}\n")


if __name__ == "__main__":
    main()
