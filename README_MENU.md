# Menu Navigator

A standalone script required to satisfy the "Navigate 5 menu links" task.

## Purpose
This script identifies the main navigation bar (`<nav>` or common menu classes) on a website and sequentially visits at least 5 links found within it.

## Usage

```bash
python menu_navigator.py --url https://www.python.org
```

## How it works
1. Opens the target URL.
2. Scans for `<nav>` tags or elements with classes like `.navbar`, `.menu`.
3. Collects all unique links.
4. Visits the first 5 links found, logging the page title for confirmation.
