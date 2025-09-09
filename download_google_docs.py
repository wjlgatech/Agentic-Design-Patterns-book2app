#!/usr/bin/env python3
"""
Script to download multiple Google Docs in various formats
"""

import os
import requests
import re
from urllib.parse import urlparse, parse_qs
import time

def extract_doc_id(url):
    """Extract Google Doc ID from various URL formats"""
    # Handle different Google Docs URL patterns
    patterns = [
        r'/document/d/([a-zA-Z0-9-_]+)',
        r'/d/([a-zA-Z0-9-_]+)',
        r'id=([a-zA-Z0-9-_]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def download_google_doc(doc_url, output_dir="downloads", formats=["pdf", "docx", "txt"]):
    """Download a Google Doc in multiple formats"""
    
    doc_id = extract_doc_id(doc_url)
    if not doc_id:
        print(f"Could not extract document ID from: {doc_url}")
        return
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Google Docs export URLs
    export_urls = {
        "pdf": f"https://docs.google.com/document/d/{doc_id}/export?format=pdf",
        "docx": f"https://docs.google.com/document/d/{doc_id}/export?format=docx",
        "txt": f"https://docs.google.com/document/d/{doc_id}/export?format=txt",
        "rtf": f"https://docs.google.com/document/d/{doc_id}/export?format=rtf",
        "odt": f"https://docs.google.com/document/d/{doc_id}/export?format=odt",
        "html": f"https://docs.google.com/document/d/{doc_id}/export?format=html",
        "epub": f"https://docs.google.com/document/d/{doc_id}/export?format=epub"
    }
    
    print(f"\nDownloading document ID: {doc_id}")
    
    for format in formats:
        if format not in export_urls:
            print(f"  Unsupported format: {format}")
            continue
            
        try:
            print(f"  Downloading as {format}...", end="", flush=True)
            response = requests.get(export_urls[format], stream=True)
            response.raise_for_status()
            
            # Generate filename
            filename = f"doc_{doc_id[:8]}.{format}"
            filepath = os.path.join(output_dir, filename)
            
            # Write to file
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f" ✓ Saved as {filename}")
            
        except requests.exceptions.RequestException as e:
            print(f" ✗ Error: {str(e)}")
        
        # Small delay to avoid rate limiting
        time.sleep(1)

def main():
    # List of Google Docs URLs to download
    # IMPORTANT: Replace these with the actual URLs from your main document
    doc_urls = [
        # Add your Google Docs URLs here
        # Example:
        # "https://docs.google.com/document/d/1rsaK53T3Lg5KoGwvf8ukOUvbELRtH-V0LnOIFDxBryE/edit",
    ]
    
    # You can also read URLs from a file
    urls_file = "google_docs_urls.txt"
    if os.path.exists(urls_file):
        print(f"Reading URLs from {urls_file}")
        with open(urls_file, 'r') as f:
            file_urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            doc_urls.extend(file_urls)
    
    if not doc_urls:
        print("No URLs to download!")
        print(f"Please add URLs to the 'doc_urls' list in this script or create '{urls_file}' with one URL per line")
        return
    
    # Download each document
    print(f"Found {len(doc_urls)} documents to download")
    
    for i, url in enumerate(doc_urls, 1):
        print(f"\n[{i}/{len(doc_urls)}] Processing: {url}")
        download_google_doc(url, formats=["pdf", "docx", "txt"])

if __name__ == "__main__":
    main()