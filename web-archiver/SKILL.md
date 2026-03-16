---
name: web_archiver
description: >
  Crawl and save websites as Markdown files. Use this skill when the user
  wants to save, download, archive, or crawl content from websites, documentation
  sites, or web pages for offline reading, analysis, or knowledge base creation —
  even if they don't explicitly mention "crawl", "scrape", "archive", or "save".
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

## How to run

```bash
web_archiver --target <URL> --output <DIR>
```

### If the `web_archiver` command fails

```bash
uv tool install --from git+https://github.com/high-u/skills.git#subdirectory=web_archiver-command web_archiver && playwright install chromium
```

The browser binary is cached globally in `~/.cache/ms-playwright/`.

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
web_archiver -t https://docs.example.com -o ./archived
```

### Limit scope for large sites

```bash
web_archiver -t https://wiki.example.com -o ./archived -m 50 -d 2
```

### Deep crawl with verbose output

```bash
web_archiver -t https://blog.example.com -o ./archived -d 5 -v
```

### Debug with JSON output

```bash
web_archiver -t https://example.com -o ./archived --json -v
```

## Notes

- Binary files (images, PDFs, videos, etc.) are automatically excluded
- Navigation, header, and footer elements are stripped
- Duplicate content across pages is automatically skipped
