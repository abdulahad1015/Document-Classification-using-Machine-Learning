
import os
from dotenv import load_dotenv
import json
from pathlib import Path
from typing import Dict, Any
import pytesseract
from PIL import Image
import google.generativeai as genai

class DocumentProcessor:
    def __init__(self, gemini_api_key: str = None):
        # Load environment variables from .env file if present
        load_dotenv()
        """
        Initialize the document processor with OCR and Gemini LLM capabilities.
        
        Args:
            gemini_api_key: API key for Google Gemini (or set GEMINI_API_KEY env var)
        """
        self.api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key required")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("models/gemini-2.5-flash")
    
    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extract text from an image using Tesseract OCR.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Extracted text as string
        """
        try:
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img)
            print(text)
            return text.strip()
        except Exception as e:
            raise Exception(f"OCR extraction failed: {str(e)}")
    
    def classify_with_llm(self, text: str, classification_prompt: str = None) -> Dict[str, Any]:
        """
        Send extracted text to Gemini LLM for classification and structured extraction.
        
        Args:
            text: The extracted text to classify
            classification_prompt: Custom prompt for classification (optional)
        Returns:
            Dictionary containing the classified data in JSON format
        """
        if not classification_prompt:
            classification_prompt = (
                """
                Analyze the following document text and extract key information.
                extract relevant fields.
                Return the results in JSON format with these fields:
                - extracted_data: (any structured data like amounts, dates, addresses)
                Document text:][[]]
                """
            )
        prompt = f"{classification_prompt}\n\n{text}\n\nProvide response in valid JSON format only."
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
            # Extract JSON from response (handles cases where LLM adds extra text)
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
            else:
                return json.loads(response_text)
        except json.JSONDecodeError as e:
            return {
                "error": "Failed to parse JSON response",
                "raw_response": response_text,
                "details": str(e)
            }
        except Exception as e:
            raise Exception(f"LLM classification failed: {str(e)}")
    
    def process_document(self, image_path: str, classification_prompt: str = None) -> Dict[str, Any]:
        """
        Complete workflow: OCR extraction + LLM classification.
        
        Args:
            image_path: Path to the document image
            classification_prompt: Custom classification prompt (optional)
            
        Returns:
            Dictionary with extracted text and classification results
        """
        print(f"Processing document: {image_path}")
        
        # Step 1: Extract text using OCR
        print("Step 1: Extracting text with OCR...")
        extracted_text = self.extract_text_from_image(image_path)
        print(f"Extracted {len(extracted_text)} characters")
        
        # Step 2: Classify with LLM
        print("Step 2: Classifying with LLM...")
        classification = self.classify_with_llm(extracted_text, classification_prompt)
        
        # Combine results
        result = {
            "source_file": image_path,
            "extracted_text": extracted_text,
            "classification": classification
        }
        
        print("Processing complete!")
        return result
    
    def save_results(self, result: Dict[str, Any], output_path: str):
        """Save results to a JSON file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Results saved to: {output_path}")


# Example usage
if __name__ == "__main__":
    # Initialize processor
    processor = DocumentProcessor()
    
    # Process a document
    image_path = "img.jpg"  # Replace with your image path
    
    # Run the complete workflow
    result = processor.process_document(
        image_path=image_path,
        classification_prompt=None  # Use default or pass custom_prompt
    )
    
    # Print results
    print("\n" + "="*50)
    print("CLASSIFICATION RESULTS:")
    print("="*50)
    print(json.dumps(result["classification"], indent=2))
    
    # Save to file
    processor.save_results(result, "output_classification.json")