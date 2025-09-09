# Google Docs Bulk Download Scripts

These scripts help you download multiple Google Docs in various formats (PDF, DOCX, TXT).

## Setup

1. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage Options

### Option 1: Interactive Batch Download (RECOMMENDED)

The simplest method - just paste your URLs:

```bash
source venv/bin/activate
python batch_download_from_list.py
```

Then paste your Google Docs URLs one per line and press Enter twice.

### Option 2: Copy & Paste Document Content

If you can access the document but the scripts can't:

1. Copy all content from the Google Doc (Ctrl+A, Ctrl+C)
2. Paste into `document_content.txt`
3. Run:

```bash
source venv/bin/activate
python parse_and_download.py
```

### Option 3: Automatic Extraction (if the main doc is public)

```bash
source venv/bin/activate
python extract_and_download_docs.py
```

### Option 4: Manual URL List

1. Add URLs to `google_docs_urls.txt` (one per line)
2. Run:

```bash
source venv/bin/activate
python download_google_docs.py
```

## Output

All downloaded files will be saved in the `downloads/` folder:
- `doc_001_12345678.pdf`
- `doc_001_12345678.docx`
- `doc_001_12345678.txt`

## Common Issues & Solutions

### "Document not accessible"
- The Google Doc needs to be publicly viewable
- Go to Share → "Anyone with the link can view"

### "Rate limit exceeded"
- The scripts include delays, but if you hit limits:
- Try downloading in smaller batches
- Wait a few minutes between batches

### "Can't extract document ID"
- Make sure URLs are in format: `https://docs.google.com/document/d/DOCUMENT_ID/...`

## Quick Start Example

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install requests beautifulsoup4

# Run interactive downloader
python batch_download_from_list.py

# Paste URLs like:
# https://docs.google.com/document/d/abc123/edit
# https://docs.google.com/document/d/def456/edit
# [Press Enter twice]

# Files will be in downloads/ folder
```

## Notes

- Scripts work with Python 3.6+
- Downloads are saved with both document ID and sequence number
- Each format is downloaded separately to handle errors gracefully
- 0.5-1 second delay between downloads to respect rate limits