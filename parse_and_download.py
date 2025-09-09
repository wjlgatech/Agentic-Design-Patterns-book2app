#!/usr/bin/env python3
"""
Script to parse Google Docs links from pasted content and download them
"""

import os
import re
import requests
import time

def extract_doc_id(url):
    """Extract Google Doc ID from various URL formats"""
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

def find_google_docs_urls(text):
    """Find all Google Docs URLs in text"""
    # Pattern to match Google Docs URLs
    pattern = r'https?://docs\.google\.com/document/[^\s\)\"\'<>]+'
    urls = re.findall(pattern, text)
    
    # Also try to find any string that looks like a doc ID after "document/d/"
    pattern2 = r'docs\.google\.com/document/d/([a-zA-Z0-9-_]+)'
    matches = re.findall(pattern2, text)
    for match in matches:
        urls.append(f"https://docs.google.com/document/d/{match}/edit")
    
    # Remove duplicates while preserving order
    seen = set()
    unique_urls = []
    for url in urls:
        doc_id = extract_doc_id(url)
        if doc_id and doc_id not in seen:
            seen.add(doc_id)
            unique_urls.append(url)
    
    return unique_urls

def download_google_doc(doc_url, doc_title="", output_dir="downloads", formats=["pdf", "docx", "txt"]):
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
    }
    
    print(f"\nDownloading document ID: {doc_id}")
    if doc_title:
        print(f"  Title: {doc_title}")
    
    for format in formats:
        if format not in export_urls:
            print(f"  Unsupported format: {format}")
            continue
            
        try:
            print(f"  Downloading as {format}...", end="", flush=True)
            response = requests.get(export_urls[format], stream=True)
            response.raise_for_status()
            
            # Generate filename
            safe_title = re.sub(r'[^\w\s-]', '', doc_title)[:30] if doc_title else "doc"
            safe_title = re.sub(r'[-\s]+', '-', safe_title)
            filename = f"{safe_title}_{doc_id[:8]}.{format}" if doc_title else f"doc_{doc_id[:8]}.{format}"
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
    print("Google Docs Link Parser and Downloader")
    print("=====================================\n")
    
    # Check if content file exists
    content_file = "document_content.txt"
    
    if os.path.exists(content_file):
        print(f"Reading content from {content_file}")
        with open(content_file, 'r') as f:
            content = f.read()
    else:
        print(f"Please create a file named '{content_file}' and paste the document content into it.")
        print("Or paste the content below (press Enter twice when done):\n")
        
        lines = []
        empty_lines = 0
        while True:
            line = input()
            if line == "":
                empty_lines += 1
                if empty_lines >= 2:
                    break
            else:
                empty_lines = 0
            lines.append(line)
        
        content = "\n".join(lines)
        
        # Save for future use
        with open(content_file, 'w') as f:
            f.write(content)
        print(f"\nContent saved to {content_file}")
    
    # Find all Google Docs URLs
    urls = find_google_docs_urls(content)
    
    if not urls:
        print("\nNo Google Docs URLs found in the content.")
        print("Make sure the URLs are in the format: https://docs.google.com/document/d/...")
        return
    
    print(f"\nFound {len(urls)} Google Docs URLs:")
    for i, url in enumerate(urls, 1):
        print(f"{i}. {url}")
    
    # Ask for confirmation
    response = input(f"\nDownload all {len(urls)} documents? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Download cancelled.")
        return
    
    # Download each document
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}]")
        download_google_doc(url)
    
    print("\n\nDownload complete!")
    print("Check the 'downloads' folder for all files")

if __name__ == "__main__":
    main()