#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "crawl4ai",
# ]
# ///
"""
Web scraping script using crawl4ai library.
Crawls a website and saves each page as a separate markdown file.
"""

import argparse
import asyncio
import hashlib
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CrawlerRunConfig,
    CacheMode,
    BFSDeepCrawlStrategy,
    DFSDeepCrawlStrategy,
    BestFirstCrawlingStrategy,
    LXMLWebScrapingStrategy,
    DefaultMarkdownGenerator,
    PruningContentFilter,
    URLPatternFilter,
    FilterChain,
)

# Minimum character count for markdown content
MIN_CHAR_COUNT = 200

# File extensions to exclude from crawling
EXCLUDED_EXTENSIONS = [
    "*.js", "*.ts", "*.css",
    "*.png", "*.jpg", "*.jpeg", "*.gif", "*.webp", "*.svg", "*.ico",
    "*.pdf", "*.doc", "*.docx", "*.xls", "*.xlsx", "*.ppt", "*.pptx",
    "*.zip", "*.tar", "*.gz", "*.rar",
    "*.mp3", "*.mp4", "*.wav", "*.avi", "*.mov",
]


def url_to_folder_name(url: str) -> str:
    """Convert URL to a safe folder name (dots and slashes to underscores)."""
    parsed = urlparse(url)
    full_path = parsed.netloc + parsed.path
    safe_name = full_path.replace(".", "_").replace("/", "_")
    safe_name = "_".join(part for part in safe_name.split("_") if part)
    return safe_name


def get_strategy(name: str, max_pages: int, max_depth: int):
    """Get deep crawl strategy with URL filtering."""
    # Create filter to exclude binary/script files
    url_filter = URLPatternFilter(
        patterns=EXCLUDED_EXTENSIONS,
        use_glob=True,
        reverse=True,  # Exclude matching patterns
    )
    filter_chain = FilterChain(filters=[url_filter])

    strategies = {
        "bfs": BFSDeepCrawlStrategy,
        "dfs": DFSDeepCrawlStrategy,
        "best-first": BestFirstCrawlingStrategy,
    }
    return strategies[name](
        max_depth=max_depth,
        max_pages=max_pages,
        filter_chain=filter_chain,
    )


async def crawl(url: str, max_pages: int, max_depth: int, strategy: str, verbose: bool):
    """Crawl website and return results."""
    browser_config = BrowserConfig(verbose=verbose)
    crawler_config = CrawlerRunConfig(
        deep_crawl_strategy=get_strategy(strategy, max_pages, max_depth),
        scraping_strategy=LXMLWebScrapingStrategy(),
        cache_mode=CacheMode.BYPASS,
        verbose=verbose,
        excluded_tags=["nav", "header", "footer"],
        markdown_generator=DefaultMarkdownGenerator(
            content_filter=PruningContentFilter(threshold=0.48),
            options={"ignore_links": True}
        ),
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=url, config=crawler_config)
        return result if isinstance(result, list) else [result]


def save_json(pages: list, output_dir: Path, verbose: bool) -> None:
    """Save crawl results as JSON file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "crawl_result.json"

    data = [page.model_dump() for page in pages]

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)

    if verbose:
        print(f"Saved JSON: {json_path}", file=sys.stderr)


def save_pages(pages: list, output_dir: Path, verbose: bool) -> int:
    """Save each page as a markdown file. Returns count of saved files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    saved = 0

    for page in pages:
        url = getattr(page, "url", "unknown")
        markdown = getattr(page, "markdown", None)
        if not markdown:
            if verbose:
                print(f"Skipping {url}: no markdown content", file=sys.stderr)
            continue

        content = getattr(markdown, "raw_markdown", "")
        if not content:
            if verbose:
                print(f"Skipping {url}: no markdown content", file=sys.stderr)
            continue

        # Skip if content is too short (character count)
        if len(content) < MIN_CHAR_COUNT:
            if verbose:
                print(f"Skipping {url}: content too short ({len(content)} chars)", file=sys.stderr)
            continue

        # Use MD5 hash of content as filename (auto-deduplication)
        filename = hashlib.md5(content.encode()).hexdigest() + ".md"
        filepath = output_dir / filename

        # Skip if file already exists (duplicate content)
        if filepath.exists():
            if verbose:
                print(f"Skipping duplicate: {url}", file=sys.stderr)
            continue

        filepath.write_text(content)

        if verbose:
            print(f"Saved: {filepath} (from {url})", file=sys.stderr)
        saved += 1

    return saved


def main():
    parser = argparse.ArgumentParser(
        description="Crawl a website and save each page as markdown"
    )
    parser.add_argument(
        "--target", "-t",
        required=True,
        help="Target URL to crawl"
    )
    parser.add_argument(
        "--output", "-o",
        required=True,
        help="Output base directory for markdown files"
    )
    parser.add_argument(
        "--max-pages", "-m",
        type=int,
        default=100,
        help="Maximum pages to crawl (default: 100)"
    )
    parser.add_argument(
        "--max-depth", "-d",
        type=int,
        default=3,
        help="Maximum crawl depth (default: 3)"
    )
    parser.add_argument(
        "--strategy", "-s",
        choices=["bfs", "dfs", "best-first"],
        default="bfs",
        help="Crawling strategy (default: bfs)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show verbose output"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output crawl results as JSON (for debugging)"
    )

    args = parser.parse_args()

    base_dir = Path(args.output)
    folder_name = url_to_folder_name(args.target)
    output_dir = base_dir / folder_name

    print(f"Crawling: {args.target}", file=sys.stderr)
    print(f"Strategy: {args.strategy}, Max pages: {args.max_pages}, Max depth: {args.max_depth}", file=sys.stderr)
    print(f"Output: {output_dir}/", file=sys.stderr)

    pages = asyncio.run(crawl(args.target, args.max_pages, args.max_depth, args.strategy, args.verbose))

    if args.json:
        save_json(pages, output_dir, args.verbose)
    saved = save_pages(pages, output_dir, args.verbose)

    print(f"Done! Saved {saved} pages to {output_dir}/", file=sys.stderr)


if __name__ == "__main__":
    main()
6
