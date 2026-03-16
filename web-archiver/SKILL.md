---
name: web-archiver
description: >
  Crawl and archive websites as Markdown files. Use this skill when the user
  wants to crawl, scrape, or archive content from websites, documentation sites,
  or web pages for analysis, archival, or knowledge base creation — even if they
  don't explicitly mention "crawl", "scrape", or "archive."
---

# Web Archiver

Crawl websites and save pages as Markdown files.

## When to use this skill

- Archiving documentation sites for offline reading
- Collecting web content for analysis or RAG pipelines
- Archiving website content as Markdown
- Extracting text from multiple pages of a website

## Requirements

- [uv](https://docs.astral.sh/uv/) must be installed
- Dependencies are resolved automatically on first run

## Before running

Confirm the script location before executing the command:

1. Check if `./scripts/archiver.py` exists
2. If not found, search for a `web-archiver` folder and check if `./scripts/archiver.py` exists within it
3. Run the command using the discovered path

## How to run

```bash
uv run ./scripts/archiver.py --target <URL> --output <DIR>
```

If the script fails with a Playwright-related error, install the browser binary:

```bash
uv run --with crawl4ai -- playwright install chromium
```

Then retry the archiving command. The browser binary is cached globally in `~/.cache/ms-playwright/`.

### Required arguments

| Argument | Description |
|----------|-------------|
| `--target, -t` | Starting URL to crawl |
| `--output, -o` | Base output directory for Markdown files |

### Optional arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--max-pages, -m` | 100 | Maximum pages to crawl |
| `--max-depth, -d` | 3 | Maximum crawl depth from start URL |
| `--strategy, -s` | bfs | Crawling strategy: `bfs`, `dfs`, or `best-first` |
| `--verbose, -v` | false | Show detailed progress |
| `--json` | false | Save raw crawl data as JSON (for debugging) |

## Crawling strategies

- **bfs** (Breadth-First Search): Crawl pages level by level. Good for comprehensive coverage.
- **dfs** (Depth-First Search): Follow links deeply before backtracking. Good for deep content trees.
- **best-first**: Prioritize pages that seem most relevant. Good for large sites where you want quality over quantity.

## Output structure

Files are saved to `<output>/<domain_path>/`:

```
output_dir/
└── example_com_docs/
    ├── a1b2c3d4e5f6.md
    ├── f6e5d4c3b2a1.md
    └── ...
```

- Folder name is derived from the target URL
- Each Markdown file is named by MD5 hash of content (auto-deduplication)
- Minimum content threshold: 200 characters

## Examples

### Crawl a documentation site

```bash
uv run ${skillDirectory}/scripts/archiver.py -t https://docs.example.com -o ./archived
```

### Limit scope for large sites

```bash
uv run ${skillDirectory}/scripts/archiver.py -t https://wiki.example.com -o ./archived -m 50 -d 2
```

### Deep crawl with verbose output

```bash
uv run ${skillDirectory}/scripts/archiver.py -t https://blog.example.com -o ./archived -d 5 -v
```

### Debug with JSON output

```bash
uv run ${skillDirectory}/scripts/archiver.py -t https://example.com -o ./archived --json -v
```

## Notes

- Binary files (images, PDFs, videos, etc.) are automatically excluded
- Navigation, header, and footer elements are stripped
- Duplicate content across pages is automatically skipped
- Dependencies are auto-resolved via uv on first run

