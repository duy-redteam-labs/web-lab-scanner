# Architecture

## Overview
Web Lab Scanner is a session-aware Python CLI scanner for lab web applications such as DVWA, Juice Shop, and similar training targets.

## High-level flow
1. CLI parses arguments or loads YAML configuration.
2. Scanner builds a shared HTTP session.
3. Scanner fetches the initial target and performs limited in-scope crawling.
4. Analyzers inspect responses and generate structured findings.
5. Reporters export JSON and HTML output artifacts.

## Core components

### CLI
- Entry point for `scan`
- Accepts target URL or YAML config
- Supports JSON and HTML output paths

### Session and HTTP layer
- Shared `requests.Session()`
- Cookie and header injection support
- Centralized fetch wrapper with basic error handling

### Crawler
- Same-host crawl only
- Breadth-first traversal
- Depth and page-count limits
- Best suited for server-rendered HTML links

### Analyzers
- `headers.py`: checks common security headers
- `cookies.py`: checks cookie flags such as HttpOnly and SameSite
- `forms.py`: extracts HTML forms and fields
- `csrf.py`: detects potentially state-changing POST forms without CSRF-like tokens
- `xss.py`: probes reflected input markers in HTML responses
- `sqli.py`: probes basic SQL error indicators after query mutation

### Reporters
- JSON report export
- HTML report export for human-readable review

## Findings model
Each finding includes:
- ID
- category
- title
- severity
- confidence
- URL
- method
- parameter
- evidence
- recommendation

## Testing strategy
- Unit tests for analyzers and helpers
- Integration tests with a controlled mock HTTP application
- End-to-end validation for reflected XSS and SQLi indicator detection

## Current limitations
- Crawler is optimized for server-rendered HTML and does not execute JavaScript
- SPA routes behind fragment identifiers or client-side rendering are not fully enumerated
- XSS and SQLi checks are heuristic indicators, not exploit confirmation
- Intended only for lab environments and authorized testing
