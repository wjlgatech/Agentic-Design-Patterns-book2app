#!/usr/bin/env python3
"""
Convert .docx files to .md with improved paragraph break handling:
- Titles and headings (with proper levels)
- Bold and italic text
- Numbered and bulleted lists (with proper resets)
- Tables (1x1 as code blocks, others as markdown tables)
- Images with references
- Proper paragraph breaks that separate lists
"""

import os
import sys
import re
import shutil
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET
import hashlib

class DocxToMarkdownConverter:
    def __init__(self, source_dir, output_dir, images_dir):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.images_dir = Path(images_dir)
        self.namespaces = {
            'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
            'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
            'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
            'pic': 'http://schemas.openxmlformats.org/drawingml/2006/picture',
            'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
        }
        self.styles = {}  # Will store style definitions
        self.numbering = {}  # Will store numbering definitions
        
    def extract_content_and_images(self, docx_path):
        """Extract text content, tables, and images from a .docx file with formatting"""
        content_elements = []
        image_mapping = {}
        
        # Create temp directory
        temp_dir = Path("temp_docx_extract")
        temp_dir.mkdir(exist_ok=True)
        
        try:
            # Extract the .docx file
            with ZipFile(docx_path, 'r') as zip_file:
                zip_file.extractall(temp_dir)
            
            # First, load styles
            self._load_styles(temp_dir)
            
            # Load numbering definitions
            self._load_numbering(temp_dir)
            
            # Extract all images and create mapping
            media_path = temp_dir / "word" / "media"
            if media_path.exists():
                for image_file in media_path.iterdir():
                    if image_file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
                        # Generate unique filename
                        doc_name = docx_path.stem.replace(" ", "_").replace(":", "")
                        image_hash = hashlib.md5(image_file.read_bytes()).hexdigest()[:8]
                        new_filename = f"{doc_name}_{image_file.stem}_{image_hash}{image_file.suffix}"
                        dest_path = self.images_dir / new_filename
                        
                        # Copy the image
                        shutil.copy2(image_file, dest_path)
                        
                        # Store mapping
                        image_mapping[image_file.name] = new_filename
                        print(f"  Extracted image: {new_filename}")
            
            # Parse relationships to map rId to image files
            rels_path = temp_dir / "word" / "_rels" / "document.xml.rels"
            rid_to_image = {}
            if rels_path.exists():
                rels_tree = ET.parse(rels_path)
                rels_root = rels_tree.getroot()
                for rel in rels_root:
                    if 'image' in rel.get('Type', ''):
                        rid = rel.get('Id')
                        target = rel.get('Target')
                        if target.startswith('media/'):
                            image_name = os.path.basename(target)
                            if image_name in image_mapping:
                                rid_to_image[rid] = image_mapping[image_name]
            
            # Parse the main document
            doc_path = temp_dir / "word" / "document.xml"
            if doc_path.exists():
                tree = ET.parse(doc_path)
                root = tree.getroot()
                
                # Process all elements in order
                body = root.find('.//w:body', self.namespaces)
                if body is not None:
                    for elem in body:
                        if elem.tag == f"{{{self.namespaces['w']}}}p":
                            # Process paragraph with formatting
                            self._process_paragraph_formatted(elem, content_elements, rid_to_image)
                        elif elem.tag == f"{{{self.namespaces['w']}}}tbl":
                            # Process table
                            self._process_table(elem, content_elements)
        
        finally:
            # Clean up temp directory
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
        
        return content_elements, image_mapping
    
    def _load_styles(self, temp_dir):
        """Load style definitions from styles.xml"""
        styles_path = temp_dir / "word" / "styles.xml"
        if styles_path.exists():
            tree = ET.parse(styles_path)
            root = tree.getroot()
            
            # Extract style definitions
            for style in root.findall('.//w:style', self.namespaces):
                style_id = style.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}styleId')
                if style_id:
                    name_elem = style.find('.//w:name', self.namespaces)
                    if name_elem is not None:
                        name = name_elem.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', '')
                        self.styles[style_id] = {
                            'name': name,
                            'type': style.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}type', '')
                        }
    
    def _load_numbering(self, temp_dir):
        """Load numbering definitions from numbering.xml"""
        numbering_path = temp_dir / "word" / "numbering.xml"
        if numbering_path.exists():
            tree = ET.parse(numbering_path)
            root = tree.getroot()
            
            # This is simplified - full implementation would need more detail
            self.numbering = {'loaded': True}
    
    def _get_paragraph_style(self, paragraph):
        """Get the style of a paragraph"""
        pPr = paragraph.find('.//w:pPr', self.namespaces)
        if pPr is not None:
            pStyle = pPr.find('.//w:pStyle', self.namespaces)
            if pStyle is not None:
                style_id = pStyle.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val')
                if style_id in self.styles:
                    return self.styles[style_id]
        return None
    
    def _get_numbering_info(self, paragraph):
        """Get numbering information for a paragraph"""
        pPr = paragraph.find('.//w:pPr', self.namespaces)
        if pPr is not None:
            numPr = pPr.find('.//w:numPr', self.namespaces)
            if numPr is not None:
                ilvl = numPr.find('.//w:ilvl', self.namespaces)
                numId = numPr.find('.//w:numId', self.namespaces)
                if ilvl is not None and numId is not None:
                    level = ilvl.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', '0')
                    num_id = numId.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', '0')
                    return {'level': int(level), 'numId': int(num_id)}
        return None
    
    def _extract_text_with_formatting(self, paragraph):
        """Extract text with inline formatting (bold, italic, etc.)"""
        formatted_text = []
        
        for run in paragraph.findall('.//w:r', self.namespaces):
            text_parts = []
            
            # Check for formatting
            rPr = run.find('.//w:rPr', self.namespaces)
            is_bold = False
            is_italic = False
            
            if rPr is not None:
                # Check for bold
                b = rPr.find('.//w:b', self.namespaces)
                if b is not None:
                    val = b.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', 'true')
                    is_bold = val != 'false'
                
                # Check for italic
                i = rPr.find('.//w:i', self.namespaces)
                if i is not None:
                    val = i.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', 'true')
                    is_italic = val != 'false'
            
            # Extract text
            for text_elem in run.findall('.//w:t', self.namespaces):
                if text_elem.text:
                    text = text_elem.text
                    
                    # Apply formatting
                    if is_bold and is_italic:
                        text = f"***{text}***"
                    elif is_bold:
                        text = f"**{text}**"
                    elif is_italic:
                        text = f"*{text}*"
                    
                    text_parts.append(text)
            
            if text_parts:
                formatted_text.append(''.join(text_parts))
        
        return ''.join(formatted_text)
    
    def _process_paragraph_formatted(self, paragraph, content_elements, rid_to_image):
        """Process a paragraph element with formatting preservation"""
        # Check if paragraph contains an image
        drawing = paragraph.find('.//w:drawing', self.namespaces)
        if drawing is not None:
            # Extract image reference
            blip = drawing.find('.//a:blip', self.namespaces)
            if blip is not None:
                embed_id = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                if embed_id and embed_id in rid_to_image:
                    image_filename = rid_to_image[embed_id]
                    content_elements.append({
                        'type': 'image',
                        'filename': image_filename,
                        'path': f"../images/{image_filename}"
                    })
        
        # Extract formatted text
        text = self._extract_text_with_formatting(paragraph)
        
        if text or drawing is None:
            # Get paragraph style
            style = self._get_paragraph_style(paragraph)
            
            # Check for numbering
            numbering = self._get_numbering_info(paragraph)
            
            # Determine element type and formatting
            element = {
                'type': 'text',
                'content': text,
                'formatting': {}
            }
            
            # Apply style-based formatting
            if style:
                style_name = style.get('name', '').lower()
                if 'title' in style_name:
                    element['type'] = 'title'
                elif 'heading 1' in style_name:
                    element['type'] = 'heading1'
                elif 'heading 2' in style_name:
                    element['type'] = 'heading2'
                elif 'heading 3' in style_name:
                    element['type'] = 'heading3'
            
            # Apply numbering
            if numbering:
                element['type'] = 'numbered_list'
                element['formatting']['level'] = numbering['level']
                element['formatting']['numId'] = numbering['numId']
            
            content_elements.append(element)
    
    def _process_table(self, table, content_elements):
        """Process a table element"""
        # Extract all rows
        rows = table.findall('.//w:tr', self.namespaces)
        
        # Check if it's a 1x1 table (one row, one cell)
        if len(rows) == 1:
            cells = rows[0].findall('.//w:tc', self.namespaces)
            if len(cells) == 1:
                # This is a 1x1 table, extract ALL its content as code
                cell_text = []
                for para in cells[0].findall('.//w:p', self.namespaces):
                    para_texts = []
                    for text_elem in para.findall('.//w:t', self.namespaces):
                        if text_elem.text:
                            para_texts.append(text_elem.text)
                    if para_texts:
                        cell_text.append(''.join(para_texts))
                
                if cell_text:
                    full_text = '\n'.join(cell_text)
                    # ALL 1x1 table content is treated as code
                    content_elements.append({
                        'type': 'code',
                        'content': full_text,
                        'language': 'python'  # Default to python
                    })
                    print(f"  Found code in 1x1 table")
                return
            else:
                # Multi-cell table, process as regular table
                self._process_regular_table(table, content_elements)
        else:
            # Multi-row table, process as regular table
            self._process_regular_table(table, content_elements)
    
    def _process_regular_table(self, table, content_elements):
        """Process a regular table (not 1x1)"""
        table_data = []
        
        for row in table.findall('.//w:tr', self.namespaces):
            row_data = []
            for cell in row.findall('.//w:tc', self.namespaces):
                cell_content = []
                for para in cell.findall('.//w:p', self.namespaces):
                    para_text = self._extract_text_with_formatting(para)
                    if para_text:
                        cell_content.append(para_text)
                row_data.append(' '.join(cell_content))
            if row_data:
                table_data.append(row_data)
        
        if table_data:
            content_elements.append({
                'type': 'table',
                'data': table_data
            })
    
    def convert_to_markdown(self, content_elements, doc_name):
        """Convert content elements to markdown format with improved paragraph handling"""
        markdown_lines = []
        
        # Track list numbering - key is numId, value is counter per level
        list_counters = {}
        prev_element = None
        in_list_context = False
        
        for i, element in enumerate(content_elements):
            current_type = element['type']
            
            # Determine if we need extra spacing
            needs_extra_space = False
            
            # If previous was a list and current is not, we might need space
            if prev_element and prev_element['type'] == 'numbered_list' and current_type != 'numbered_list':
                # Check if this is a meaningful paragraph (not empty)
                if current_type == 'text' and element['content'].strip():
                    needs_extra_space = True
                    # Also reset list counters when we have a meaningful paragraph after a list
                    list_counters = {}
                    in_list_context = False
            
            # If we're transitioning from non-list to list, check if we should continue or reset
            if current_type == 'numbered_list' and prev_element and prev_element['type'] != 'numbered_list':
                # If the previous element was a substantial text paragraph, treat this as a new list
                if prev_element['type'] == 'text' and prev_element['content'].strip():
                    # Check if the text looks like it's introducing a new list
                    text_lower = prev_element['content'].strip().lower()
                    if any(phrase in text_lower for phrase in ['could instead:', 'might:', 'approach:', 'following:', 'these:']):
                        # This looks like a new list introduction, ensure we have fresh numbering
                        numId = element['formatting'].get('numId', 0)
                        if numId in list_counters:
                            del list_counters[numId]
                        in_list_context = True
            
            # Add extra space before this element if needed
            if needs_extra_space and markdown_lines and markdown_lines[-1] != '':
                markdown_lines.append('')
            
            if element['type'] == 'title':
                # Main title (use single #)
                markdown_lines.append(f"# {element['content']}")
                markdown_lines.append('')
                
            elif element['type'] == 'heading1':
                # Heading 1 (use ##)
                markdown_lines.append(f"## {element['content']}")
                markdown_lines.append('')
                
            elif element['type'] == 'heading2':
                # Heading 2 (use ###)
                markdown_lines.append(f"### {element['content']}")
                markdown_lines.append('')
                
            elif element['type'] == 'heading3':
                # Heading 3 (use ####)
                markdown_lines.append(f"#### {element['content']}")
                markdown_lines.append('')
                
            elif element['type'] == 'numbered_list':
                # Numbered list item
                level = element['formatting'].get('level', 0)
                numId = element['formatting'].get('numId', 0)
                indent = '   ' * level
                
                # Initialize counters for this numId if needed
                if numId not in list_counters:
                    list_counters[numId] = {}
                
                # Initialize or increment counter for this level
                if level not in list_counters[numId]:
                    list_counters[numId][level] = 0
                list_counters[numId][level] += 1
                
                # Clear higher level counters
                for l in list(list_counters[numId].keys()):
                    if l > level:
                        del list_counters[numId][l]
                
                markdown_lines.append(f"{indent}{list_counters[numId][level]}. {element['content']}")
                in_list_context = True
                
            elif element['type'] == 'text':
                # Regular text
                if element['content'].strip():
                    markdown_lines.append(element['content'])
                    # Only add blank line after text if it's not followed by a list
                    next_elem = content_elements[i + 1] if i + 1 < len(content_elements) else None
                    if next_elem and next_elem['type'] != 'numbered_list':
                        markdown_lines.append('')
                elif not in_list_context:
                    # Empty line outside of list context
                    markdown_lines.append('')
                    
            elif element['type'] == 'image':
                # Image reference
                markdown_lines.append(f"![{element['filename']}]({element['path']})")
                markdown_lines.append('')
                
            elif element['type'] == 'code':
                # Code block
                code = element['content']
                # Remove markdown code fences if they exist in the content
                code = code.replace('```python', '').replace('```', '')
                code = code.strip()
                
                # Add code block
                markdown_lines.append(f"```{element['language']}")
                markdown_lines.append(code)
                markdown_lines.append("```")
                markdown_lines.append('')
                
            elif element['type'] == 'table':
                # Markdown table
                if element['data']:
                    # Add table headers (first row)
                    markdown_lines.append('| ' + ' | '.join(element['data'][0]) + ' |')
                    # Add separator
                    markdown_lines.append('| ' + ' | '.join(['---' for _ in element['data'][0]]) + ' |')
                    # Add remaining rows
                    for row in element['data'][1:]:
                        markdown_lines.append('| ' + ' | '.join(row) + ' |')
                    markdown_lines.append('')
            
            # Update previous element
            prev_element = element
        
        # Clean up any duplicate empty lines
        cleaned_lines = []
        prev_empty = False
        for line in markdown_lines:
            if line == '':
                if not prev_empty:
                    cleaned_lines.append(line)
                prev_empty = True
            else:
                cleaned_lines.append(line)
                prev_empty = False
        
        return '\n'.join(cleaned_lines)
    
    def convert_file(self, docx_path):
        """Convert a single .docx file to markdown"""
        print(f"\nProcessing: {docx_path.name}")
        
        try:
            # Extract content and images
            content_elements, image_mapping = self.extract_content_and_images(docx_path)
            
            # Convert to markdown
            markdown_content = self.convert_to_markdown(content_elements, docx_path.stem)
            
            # Write markdown file
            output_path = self.output_dir / f"{docx_path.stem}.md"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            print(f"  Created: {output_path.name}")
            
            if image_mapping:
                print(f"  Extracted {len(image_mapping)} images")
                
        except Exception as e:
            print(f"  Error converting {docx_path.name}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def convert_all(self):
        """Convert all .docx files in the source directory"""
        docx_files = sorted(self.source_dir.glob("*.docx"))
        
        if not docx_files:
            print("No .docx files found in source directory")
            return
        
        print(f"Found {len(docx_files)} files to convert")
        
        for docx_file in docx_files:
            self.convert_file(docx_file)

def main():
    # Setup directories
    source_dir = "/Users/paulwu/Projects/Agentic-Design-Patterns-book2app/book"
    output_dir = "/Users/paulwu/Projects/Agentic-Design-Patterns-book2app/book_md" 
    images_dir = "/Users/paulwu/Projects/Agentic-Design-Patterns-book2app/images"
    
    # Create converter and run
    converter = DocxToMarkdownConverter(source_dir, output_dir, images_dir)
    converter.convert_all()
    
    print("\nConversion complete!")

if __name__ == "__main__":
    main()