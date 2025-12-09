import os,json
from pathlib import Path
from typing import List, Dict, Any
from paddleocr import PaddleOCR
from dotenv import load_dotenv
import google.generativeai as genai


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
            "raw_text": extracted_text
        }
        
        return result

class LLMClassifier:
    def __init__(self, gemini_api_key: str = None, temperature: float = 0):

        load_dotenv()
        
        self.api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key required. Set GEMINI_API_KEY in .env or pass as argument.")
        
        genai.configure(api_key=self.api_key)
        self.temperature = temperature
        
        # Initialize model with generation config
        generation_config = genai.GenerationConfig(
            temperature=self.temperature,
            top_p=0,
            top_k=1,
            max_output_tokens=2048,
        )
        
        # Configure safety settings to be less restrictive
        # This prevents blocking legitimate document content
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            }
        ]
        
        self.model = genai.GenerativeModel(
            model_name="models/gemini-2.5-flash",
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
    
    def classify_text(self, text: str, classification_prompt: str = None) -> Dict[str, Any]:
        if not text or text.strip() == "":
            return {
                "document_type": "empty_document",
                "extracted_data": {},
                "field_names": []
            }
        
        if not classification_prompt:
            classification_prompt = """
            Analyze the following document text and extract key information.
            Identify ALL field names/labels present in the document.
            
            Return the results in JSON format with these fields:
            - document_type: (e.g., "ID Card", "Passport", etc.)
            - classified_data: (dictionary of field_name: field_value pairs)
            - field_names: (list of just the field names for clustering purposes)
            - identifier: (name of a key field to identify the document, e.g., "ID Number")
            
            Document text:
            """
        
        prompt = f"{classification_prompt}\n\n{text}\n\nProvide response in valid JSON format only. Do not wrap in markdown code blocks."
        
        try:
            response = self.model.generate_content(prompt)
            if not response.parts:
                print(f"Warning: Empty response from LLM. -- {response.promptFeedback}")
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present (```json ... ``` or ``` ... ```)
            if response_text.startswith("```"):
                # Find the first newline after opening ```
                first_newline = response_text.find('\n')
                if first_newline != -1:
                    response_text = response_text[first_newline + 1:]
                # Remove closing ```
                if response_text.endswith("```"):
                    response_text = response_text[:-3].strip()
            
            # Extract JSON from response (handles cases where LLM adds extra text)
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                parsed_json = json.loads(json_str)
                
                # Ensure required fields exist
                if "field_names" not in parsed_json:
                    parsed_json["field_names"] = list(parsed_json.get("extracted_data", {}).keys())
                
                return parsed_json
            else:
                return json.loads(response_text)
                
        except json.JSONDecodeError as e:
            # Try to salvage partial response
            print(f"Warning: JSON parsing failed, attempting to salvage partial data...")
            try:
                # If response was truncated, try to close it properly
                json_start = response_text.find('{')
                if json_start != -1:
                    # Count braces to see if it's balanced
                    open_braces = response_text.count('{')
                    close_braces = response_text.count('}')
                    
                    if open_braces > close_braces:
                        # Try to close unbalanced braces
                        response_text = response_text + ('}' * (open_braces - close_braces))
                        return json.loads(response_text[json_start:])
            except:
                pass
            
            return {
                "error": "Failed to parse JSON response",
                "raw_response": response_text[:500],  # Limit to first 500 chars
                "details": str(e)
            }
        except Exception as e:
            return {
                "error": "LLM classification failed",
                "details": str(e)
            }
    
    def classify_document(self, document: Dict[str, Any], classification_prompt: str = None) -> Dict[str, Any]:
        """
        Classify a single document that already has OCR text extracted.
        
        Args:
            document: Dictionary with 'extracted_text' and other metadata
            classification_prompt: Custom prompt for classification (optional)
            
        Returns:
            Document dictionary with added 'classification' field
        """
        extracted_text = document.get("raw_text", "")
        print(f"Classifying: {document.get('file_name', 'unknown')}")
        
        extracted_data = self.classify_text(extracted_text, classification_prompt)
        
        # Add classification to document
        document['extracted_text'] = extracted_data.get("classified_data", {})
        document['field_names'] = extracted_data.get("field_names", [])
        document['identifier'] = extracted_data.get("identifier", "")
        return document


def process_single_image(image_path: str):

    if not os.path.exists(image_path):
        print(f"Error: Image file '{image_path}' not found.")
        return
    ocr_processor = OCRProcessor()
    ocr_result = ocr_processor.process_single_document(image_path)
    
    try:
        classifier = LLMClassifier(temperature=1)
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set GEMINI_API_KEY in .env file or environment variable")
        return
    
    classified_document = classifier.classify_document(ocr_result)
    return classified_document
    

if __name__ == "__main__":
    result = process_single_image("images/id1.jpg")
    print(result)
    with open("results/ocr_llm.json", "w") as f:
        json.dump(result, f, indent=4)