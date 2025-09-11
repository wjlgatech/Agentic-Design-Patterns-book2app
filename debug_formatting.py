#!/usr/bin/env python3
"""
Debug script to check text formatting in Chapter 3
"""

from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET

def debug_chapter3_formatting():
    """Check the actual formatting of text in Chapter 3"""
    
    namespaces = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
        'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
    }
    
    docx_path = Path("/Users/paulwu/Projects/Agentic-Design-Patterns-book2app/book/Chapter 3_ Parallelization.docx")
    temp_dir = Path("temp_debug")
    temp_dir.mkdir(exist_ok=True)
    
    # Extract the .docx file
    with ZipFile(docx_path, 'r') as zip_file:
        zip_file.extractall(temp_dir)
    
    # Parse the main document
    doc_path = temp_dir / "word" / "document.xml"
    tree = ET.parse(doc_path)
    root = tree.getroot()
    
    # Find the first few paragraphs
    body = root.find('.//w:body', namespaces)
    para_count = 0
    
    for para in body.findall('.//w:p', namespaces):
        if para_count >= 10:  # Check first 10 paragraphs
            break
            
        # Extract text and check for italic formatting
        full_text = []
        has_italic = False
        
        for run in para.findall('.//w:r', namespaces):
            # Check for italic
            rPr = run.find('.//w:rPr', namespaces)
            if rPr is not None:
                i = rPr.find('.//w:i', namespaces)
                if i is not None:
                    val = i.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', 'true')
                    if val != 'false':
                        has_italic = True
            
            # Get text
            for text_elem in run.findall('.//w:t', namespaces):
                if text_elem.text:
                    full_text.append(text_elem.text)
        
        text_content = ''.join(full_text)
        if text_content.strip():
            para_count += 1
            print(f"\nParagraph {para_count}:")
            print(f"Text: {text_content[:100]}...")
            print(f"Has italic formatting in Word: {has_italic}")
            
            # Check if this text contains our target phrase
            if "In the previous chapters" in text_content:
                print("*** FOUND TARGET PARAGRAPH ***")
                print(f"Full text: {text_content}")
                print(f"Italic in Word document: {has_italic}")
    
    # Clean up
    import shutil
    shutil.rmtree(temp_dir)

if __name__ == "__main__":
    debug_chapter3_formatting()