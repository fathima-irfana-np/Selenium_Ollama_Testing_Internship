# Selenium Ollama Scraper

A recursive web scraper that navigates a website, extracts text content, and uses a local Ollama LLM to summarize each page.

## Features

- **Recursive Navigation**: Starts from a base URL and follows internal links up to a specified depth (default: 10 pages).
- **Intelligent Scraper**: Uses Selenium to render pages and BeautifulSoup to extract clean text (ignoring scripts/styles).
- **Local AI Power**: Uses [Ollama](https://ollama.com/) running locally to generate concise summaries.
- **Structured Output**: Saves results as a JSON file (`summary_report.json`).

## Prerequisites

1. **Python 3.8+**
2. **Google Chrome** or **Edge** installed.
3. **Ollama**: Installed and running locally.

## Setup

1. **Install Ollama**
   - Download from [ollama.com](https://ollama.com).
   - Pull a model (e.g., mistral):
     ```bash
     ollama pull mistral
     ```
   - Start the server:
     ```bash
     ollama serve
     ```

2. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the scraper providing the target URL:

```bash
python main.py --url "https://example.com"
```

### Optional Arguments

- `--model`: Specify the Ollama model to use (default: `mistral`).
- `--headless`: Run the browser in background (headless mode).
- `--depth`: Number of unique pages to visit (default: `10`).

### Example

```bash
# Run headless with llama3 model for 5 pages
python main.py --url "https://news.ycombinator.com" --model "llama3" --headless --depth 5
```

## Output

The script creates `summary_report.json` in the current directory:

```json
{
    "https://example.com": "This page describes domain examples...",
    "https://example.com/more": "Further details about the domain..."
}
```

## Troubleshooting

- **Ollama Connection Error**: Ensure `ollama serve` is running and accessible at `http://localhost:11434`.
- **WebDriver Error**: The script uses `webdriver-manager` to automatically handle drivers. If it fails, ensure your Chrome/Edge browser is up to date.
