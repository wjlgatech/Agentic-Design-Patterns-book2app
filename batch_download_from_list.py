#!/usr/bin/env python3
"""
Simple batch downloader - just paste your Google Docs URLs
"""

import os
import requests
import re
import time

def extract_doc_id(url):
    """Extract Google Doc ID from URL"""
    patterns = [
        r'/document/d/([a-zA-Z0-9-_]+)',
        r'/d/([a-zA-Z0-9-_]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def download_doc(doc_id, index, total):
    """Download a single Google Doc"""
    print(f"\n[{index}/{total}] Downloading doc ID: {doc_id[:8]}...")
    
    os.makedirs("downloads", exist_ok=True)
    
    formats = {
        "pdf": f"https://docs.google.com/document/d/{doc_id}/export?format=pdf",
        "docx": f"https://docs.google.com/document/d/{doc_id}/export?format=docx",
        "txt": f"https://docs.google.com/document/d/{doc_id}/export?format=txt"
    }
    
    success_count = 0
    for fmt, url in formats.items():
        try:
            print(f"  Downloading {fmt}...", end="", flush=True)
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            filename = f"downloads/doc_{index:03d}_{doc_id[:8]}.{fmt}"
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            print(f" ✓")
            success_count += 1
            time.sleep(0.5)  # Be nice to Google's servers
            
        except Exception as e:
            print(f" ✗ ({str(e)[:50]}...)")
    
    return success_count > 0

def main():
    print("Google Docs Batch Downloader")
    print("===========================\n")
    print("Paste Google Docs URLs below (one per line)")
    print("Press Enter twice when done:\n")
    
    urls = []
    empty_lines = 0
    
    while True:
        line = input().strip()
        if not line:
            empty_lines += 1
            if empty_lines >= 2:
                break
        else:
            empty_lines = 0
            if 'docs.google.com' in line:
                urls.append(line)
    
    if not urls:
        print("\nNo Google Docs URLs found!")
        return
    
    print(f"\nFound {len(urls)} Google Docs URLs")
    
    # Extract doc IDs
    doc_ids = []
    for url in urls:
        doc_id = extract_doc_id(url)
        if doc_id:
            doc_ids.append(doc_id)
        else:
            print(f"Warning: Could not extract ID from: {url}")
    
    if not doc_ids:
        print("\nNo valid document IDs found!")
        return
    
    print(f"Ready to download {len(doc_ids)} documents")
    response = input("\nProceed? (y/n): ")
    
    if response.lower() != 'y':
        print("Cancelled.")
        return
    
    # Download documents
    success = 0
    for i, doc_id in enumerate(doc_ids, 1):
        if download_doc(doc_id, i, len(doc_ids)):
            success += 1
    
    print(f"\n\nDownload complete!")
    print(f"Successfully downloaded: {success}/{len(doc_ids)} documents")
    print(f"Files saved in: downloads/")

if __name__ == "__main__":
    main()