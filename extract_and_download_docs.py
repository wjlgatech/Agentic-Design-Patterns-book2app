#!/usr/bin/env python3
"""
Script to extract Google Docs links from a main document and download them all
"""

import os
import requests
import re
from bs4 import BeautifulSoup
import time
from urllib.parse import urlparse
import json

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

def get_google_doc_content(doc_id):
    """Get the content of a Google Doc as HTML"""
    # Try to get the published version
    urls_to_try = [
        f"https://docs.google.com/document/d/{doc_id}/pub",
        f"https://docs.google.com/document/d/{doc_id}/preview",
        f"https://docs.google.com/document/d/{doc_id}/export?format=html",
        f"https://docs.google.com/document/d/{doc_id}/edit"
    ]
    
    for url in urls_to_try:
        try:
            print(f"  Trying URL: {url}")
            response = requests.get(url)
            print(f"  Response status: {response.status_code}")
            if response.status_code == 200:
                # Save a sample for debugging
                with open("debug_content.html", "w") as f:
                    f.write(response.text[:5000])  # First 5000 chars
                return response.text
        except Exception as e:
            print(f"  Error: {e}")
            continue
    
    return None

def extract_google_docs_links(html_content):
    """Extract all Google Docs links from HTML content"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all links
    links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if 'docs.google.com/document' in href:
            # Clean up the URL
            if href.startswith('/'):
                href = 'https://docs.google.com' + href
            links.append({
                'url': href,
                'text': a.get_text(strip=True),
                'doc_id': extract_doc_id(href)
            })
    
    # Remove duplicates based on doc_id
    unique_links = []
    seen_ids = set()
    for link in links:
        if link['doc_id'] and link['doc_id'] not in seen_ids:
            seen_ids.add(link['doc_id'])
            unique_links.append(link)
    
    return unique_links

def download_google_doc(doc_info, output_dir="downloads", formats=["pdf", "docx", "txt"]):
    """Download a Google Doc in multiple formats"""
    
    doc_id = doc_info['doc_id']
    doc_title = doc_info.get('text', 'Untitled')
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Google Docs export URLs
    export_urls = {
        "pdf": f"https://docs.google.com/document/d/{doc_id}/export?format=pdf",
        "docx": f"https://docs.google.com/document/d/{doc_id}/export?format=docx",
        "txt": f"https://docs.google.com/document/d/{doc_id}/export?format=txt",
        "md": f"https://docs.google.com/document/d/{doc_id}/export?format=txt"  # Will convert to MD
    }
    
    print(f"\nDownloading: {doc_title}")
    print(f"  Doc ID: {doc_id}")
    
    # Clean filename
    safe_title = re.sub(r'[^\w\s-]', '', doc_title)[:50]
    safe_title = re.sub(r'[-\s]+', '-', safe_title)
    
    downloaded_files = []
    
    for format in formats:
        if format not in export_urls:
            print(f"  Unsupported format: {format}")
            continue
            
        try:
            print(f"  Downloading as {format}...", end="", flush=True)
            response = requests.get(export_urls[format], stream=True)
            response.raise_for_status()
            
            # Generate filename
            filename = f"{safe_title}_{doc_id[:8]}.{format}"
            filepath = os.path.join(output_dir, filename)
            
            # Write to file
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f" ✓ Saved as {filename}")
            downloaded_files.append(filepath)
            
        except requests.exceptions.RequestException as e:
            print(f" ✗ Error: {str(e)}")
        
        # Small delay to avoid rate limiting
        time.sleep(1)
    
    return downloaded_files

def create_index(doc_links, output_dir="downloads"):
    """Create an index file with all downloaded documents"""
    index_path = os.path.join(output_dir, "index.json")
    with open(index_path, 'w') as f:
        json.dump(doc_links, f, indent=2)
    
    # Also create a markdown index
    md_index_path = os.path.join(output_dir, "index.md")
    with open(md_index_path, 'w') as f:
        f.write("# Downloaded Google Docs Index\n\n")
        for i, doc in enumerate(doc_links, 1):
            f.write(f"{i}. [{doc['text']}]({doc['url']})\n")
            f.write(f"   - Doc ID: {doc['doc_id']}\n\n")

def main():
    # Main document containing links
    main_doc_url = "https://docs.google.com/document/d/1rsaK53T3Lg5KoGwvf8ukOUvbELRtH-V0LnOIFDxBryE/edit"
    
    print(f"Extracting links from main document: {main_doc_url}")
    
    # Extract the main document ID
    main_doc_id = extract_doc_id(main_doc_url)
    if not main_doc_id:
        print("Error: Could not extract document ID from main URL")
        return
    
    # Get the main document content
    print(f"Fetching content from document ID: {main_doc_id}")
    html_content = get_google_doc_content(main_doc_id)
    
    if not html_content:
        print("Error: Could not fetch document content")
        print("Please ensure the document is publicly accessible or try the manual method")
        return
    
    # Extract all Google Docs links
    print("Extracting Google Docs links...")
    doc_links = extract_google_docs_links(html_content)
    
    if not doc_links:
        print("No Google Docs links found in the document")
        print("The document might not be publicly accessible")
        return
    
    print(f"\nFound {len(doc_links)} Google Docs links:")
    for i, doc in enumerate(doc_links, 1):
        print(f"{i}. {doc['text']} ({doc['doc_id']})")
    
    # Create index
    create_index(doc_links)
    
    # Download each document
    print(f"\nStarting download of {len(doc_links)} documents...")
    
    for i, doc in enumerate(doc_links, 1):
        print(f"\n[{i}/{len(doc_links)}]", end="")
        download_google_doc(doc, formats=["pdf", "docx", "txt"])
    
    print("\n\nDownload complete!")
    print("Check the 'downloads' folder for all files")
    print("See 'downloads/index.md' for a list of all downloaded documents")

if __name__ == "__main__":
    main()