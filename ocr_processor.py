"""
OCR Processing Module
Handles text extraction from images using PaddleOCR.
"""
import os
import json
from pathlib import Path
from typing import List, Dict, Any
from paddleocr import PaddleOCR
import numpy as np
from PIL import Image


class OCRProcessor:
    def __init__(self, use_angle_cls=True, lang='en', use_gpu=False):

        print("Initializing PaddleOCR...")
        self.ocr = PaddleOCR(
            use_angle_cls=use_angle_cls,
            lang=lang,
            use_gpu=use_gpu,
            show_log=False  # Suppress verbose logging
        )
        print("PaddleOCR initialized successfully")
    
    def extract_text_from_image(self, image_path: str) -> str:

        try:
            # PaddleOCR can work directly with image paths
            result = self.ocr.ocr(image_path, cls=True)
            
            # Extract text from results
            # PaddleOCR returns: [[[box], (text, confidence)], ...]
            extracted_lines = []
            
            if result and result[0]:
                for line in result[0]:
                    if line and len(line) >= 2:
                        text = line[1][0]  # Get text (second element, first item)
                        confidence = line[1][1]  # Get confidence score
                        extracted_lines.append(text)
            
            # Join all lines with newline
            full_text = '\n'.join(extracted_lines)
            
            print(f"Extracted text from {Path(image_path).name}: {len(full_text)} characters")
            return full_text.strip()
            
        except Exception as e:
            print(f"Error extracting text from {image_path}: {str(e)}")
            return ""
    
    def process_single_document(self, image_path: str) -> Dict[str, Any]:

        print(f"Processing: {image_path}")
        extracted_text = self.extract_text_from_image(image_path)
        
        result = {
            "source_file": image_path,
            "file_name": Path(image_path).name,
            "extracted_text": extracted_text
        }
        
        return result
    
    def process_multiple_documents(self, image_paths: List[str]) -> List[Dict[str, Any]]:

        results = []
        
        print(f"\nProcessing {len(image_paths)} documents with OCR...")
        for path in image_paths:
            try:
                result = self.process_single_document(path)
                results.append(result)
            except Exception as e:
                print(f"Error processing {path}: {str(e)}")
                continue
        
        print(f"\nSuccessfully processed {len(results)} documents")
        return results
    
    def save_results(self, results: List[Dict[str, Any]], output_path: str):
        """Save OCR results to a JSON file."""
        output_data = {
            "total_documents": len(results),
            "documents": results
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print(f"OCR results saved to: {output_path}")
    
    def load_results(self, input_path: str) -> List[Dict[str, Any]]:
        """Load OCR results from a JSON file."""
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"Loaded {data['total_documents']} documents from {input_path}")
        return data['documents']


if __name__ == "__main__":
    import sys
    
    # Initialize PaddleOCR with English language
    # For other languages, use: lang='ch' (Chinese), 'french', 'german', 'korean', 'japan', etc.
    # For GPU support: use_gpu=True
    processor = OCRProcessor(use_angle_cls=True, lang='en', use_gpu=True)
    
    if len(sys.argv) > 1:
        if os.path.isdir(sys.argv[1]):
            image_dir = sys.argv[1]
            image_paths = [
                os.path.join(image_dir, f) 
                for f in os.listdir(image_dir) 
                if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff'))
            ]
        else:
            image_paths = sys.argv[1:]
    else:
        image_dir = "images"
        if os.path.exists(image_dir):
            image_paths = [
                os.path.join(image_dir, f) 
                for f in os.listdir(image_dir) 
                if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff'))
            ]
        else:
            print(f"Error: '{image_dir}' directory not found.")
            print("Usage: python ocr_processor.py [image_dir or image_files...]")
            sys.exit(1)
    
    results = processor.process_multiple_documents(image_paths)
    
    processor.save_results(results, "results/ocr_results.json")
    
    print("\nOCR processing complete!")
