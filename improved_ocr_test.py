#!/usr/bin/env python3
"""
Improved OCR test with better configuration and preprocessing.
"""

import os
import zipfile
import shutil
from pathlib import Path
from docx import Document
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract

def preprocess_image(image_path, output_path):
    """Preprocess image to improve OCR accuracy."""
    with Image.open(image_path) as img:
        # Convert to RGB if needed
        if img.mode == 'RGBA':
            # Create white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])  # Use alpha as mask
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize if too small
        width, height = img.size
        if width < 1000 or height < 800:
            scale = max(1000/width, 800/height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            img = img.resize((new_width, new_height), Image.LANCZOS)
        
        # Enhance contrast and sharpness
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.5)
        
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(2.0)
        
        # Convert to grayscale
        img = img.convert('L')
        
        # Save preprocessed image
        img.save(output_path)
        return img

def extract_images_from_docx(docx_path, temp_dir):
    """Extract all images from a .docx file."""
    images = []
    
    with zipfile.ZipFile(docx_path, 'r') as docx_zip:
        for file_info in docx_zip.filelist:
            if file_info.filename.startswith('word/media/') and any(
                file_info.filename.lower().endswith(ext) 
                for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff']
            ):
                image_name = os.path.basename(file_info.filename)
                temp_image_path = os.path.join(temp_dir, image_name)
                
                with docx_zip.open(file_info.filename) as source_file:
                    with open(temp_image_path, 'wb') as target_file:
                        target_file.write(source_file.read())
                
                images.append(temp_image_path)
    
    return images

def test_ocr_with_different_configs(image_path):
    """Test OCR with different Tesseract configurations."""
    results = {}
    
    # Different PSM (Page Segmentation Mode) options for code
    configs = [
        '--psm 6',  # Uniform block of text
        '--psm 4',  # Single column of text
        '--psm 1',  # Automatic page segmentation with OSD
        '--psm 3',  # Fully automatic page segmentation
        '--psm 8',  # Single word
        '--psm 13', # Raw line. Treat the image as a single text line
        '-c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+-=[]{}|;:,.<>?/\\\'\" \n\t',  # Code characters
    ]
    
    print("Testing different OCR configurations:")
    for i, config in enumerate(configs):
        try:
            text = pytesseract.image_to_string(Image.open(image_path), config=config)
            results[f"Config {i+1} ({config})"] = text
            print(f"  Config {i+1}: {len(text)} chars extracted")
        except Exception as e:
            results[f"Config {i+1} ({config})"] = f"Error: {e}"
            print(f"  Config {i+1}: Failed - {e}")
    
    return results

def test_multiple_files():
    """Test OCR on multiple files to find which ones have code images."""
    book_dir = Path("book")
    temp_dir = "temp_images_test"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Test first 5 files
    docx_files = list(book_dir.glob("*.docx"))[:5]
    
    print(f"Testing {len(docx_files)} files for images...")
    
    all_results = []
    
    for docx_file in docx_files:
        print(f"\n=== Testing {docx_file.name} ===")
        
        images = extract_images_from_docx(docx_file, temp_dir)
        
        if not images:
            print("  No images found")
            continue
        
        print(f"  Found {len(images)} images")
        
        for i, image_path in enumerate(images[:2]):  # Test first 2 images per file
            print(f"\n  --- Image {i+1}: {os.path.basename(image_path)} ---")
            
            # Preprocess image
            preprocessed_path = os.path.join(temp_dir, f"preprocessed_{os.path.basename(image_path)}")
            try:
                preprocess_image(image_path, preprocessed_path)
                print(f"    Preprocessed image saved")
            except Exception as e:
                print(f"    Preprocessing failed: {e}")
                preprocessed_path = image_path
            
            # Test OCR configurations
            results = test_ocr_with_different_configs(preprocessed_path)
            
            # Find best result
            best_config = ""
            best_text = ""
            max_length = 0
            
            for config, text in results.items():
                if isinstance(text, str) and not text.startswith("Error:"):
                    if len(text) > max_length:
                        max_length = len(text)
                        best_text = text
                        best_config = config
            
            if best_text.strip():
                print(f"    Best result: {best_config}")
                print(f"    Text preview: {best_text[:100]}...")
                
                # Save full result
                result_file = f"ocr_result_{docx_file.stem}_{i+1}.txt"
                with open(result_file, "w") as f:
                    f.write(f"File: {docx_file.name}\n")
                    f.write(f"Image: {os.path.basename(image_path)}\n")
                    f.write(f"Best config: {best_config}\n")
                    f.write("="*50 + "\n")
                    f.write(best_text)
                
                all_results.append({
                    'file': docx_file.name,
                    'image': os.path.basename(image_path),
                    'config': best_config,
                    'text_length': len(best_text),
                    'result_file': result_file
                })
            else:
                print("    No text extracted with any configuration")
    
    # Summary
    print(f"\n=== SUMMARY ===")
    print(f"Found {len(all_results)} images with extractable text:")
    for result in all_results:
        print(f"  {result['file']} -> {result['image']} ({result['text_length']} chars)")
    
    # Clean up
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    test_multiple_files()