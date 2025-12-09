"""
LLM Classification Module
Handles document classification using Google Gemini API.
"""
import os
import json
from dotenv import load_dotenv
from typing import Dict, Any, List
import google.generativeai as genai


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
        """
        Send extracted text to Gemini LLM for classification and structured extraction.
        
        Args:
            text: The extracted text to classify
            classification_prompt: Custom prompt for classification (optional)
            
        Returns:
            Dictionary containing the classified data in JSON format
        """
        if not text or text.strip() == "":
            return {
                "document_type": "empty_document",
                "extracted_data": {},
                "field_names_only": []
            }
        
        if not classification_prompt:
            classification_prompt = """
            Analyze the following document text and extract key information.
            Identify ALL field names/labels present in the document.
            
            Return the results in JSON format with these fields:
            - document_type: (e.g., invoice, receipt, contract, letter, form, etc.)
            - extracted_data: (dictionary of field_name: field_value pairs)
            - field_names_only: (list of just the field names for clustering purposes)
            
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
                if "field_names_only" not in parsed_json:
                    parsed_json["field_names_only"] = list(parsed_json.get("extracted_data", {}).keys())
                
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
        extracted_text = document.get("extracted_text", "")
        print(f"Classifying: {document.get('file_name', 'unknown')}")
        
        classification = self.classify_text(extracted_text, classification_prompt)
        
        # Add classification to document
        document["classification"] = classification
        return document
    
    def classify_multiple_documents(self, documents: List[Dict[str, Any]], 
                                   classification_prompt: str = None) -> List[Dict[str, Any]]:
        """
        Classify multiple documents that already have OCR text extracted.
        
        Args:
            documents: List of document dictionaries with 'extracted_text'
            classification_prompt: Custom prompt for classification (optional)
            
        Returns:
            List of documents with added 'classification' fields
        """
        print(f"\nClassifying {len(documents)} documents with LLM...")
        
        classified_docs = []
        for doc in documents:
            try:
                classified_doc = self.classify_document(doc, classification_prompt)
                classified_docs.append(classified_doc)
            except Exception as e:
                print(f"Error classifying {doc.get('file_name', 'unknown')}: {str(e)}")
                doc["classification"] = {
                    "error": "Classification failed",
                    "details": str(e)
                }
                classified_docs.append(doc)
        
        print(f"\nSuccessfully classified {len(classified_docs)} documents")
        return classified_docs
    
    def save_results(self, documents: List[Dict[str, Any]], output_path: str):
        """Save classification results to a JSON file."""
        output_data = {
            "total_documents": len(documents),
            "documents": documents
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print(f"Classification results saved to: {output_path}")
    
    def load_ocr_results(self, input_path: str) -> List[Dict[str, Any]]:
        """Load OCR results from a JSON file."""
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"Loaded {data['total_documents']} documents from {input_path}")
        return data['documents']


if __name__ == "__main__":
    import sys
    
    # Parse temperature from command line if provided
    temperature = 0.1  # Default temperature
    if len(sys.argv) > 2:
        try:
            temperature = float(sys.argv[2])
            if not 0.0 <= temperature <= 2.0:
                print(f"Warning: Temperature {temperature} is outside recommended range [0.0-2.0]")
        except ValueError:
            print(f"Warning: Invalid temperature value '{sys.argv[2]}', using default 0.1")
    
    try:
        classifier = LLMClassifier(temperature=temperature)
        print(f"Using temperature: {temperature}")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = "results/ocr_results.json"
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        print("Usage: python llm_classifier.py [ocr_results.json] [temperature]")
        print("  temperature: 0.0-2.0 (default: 0.1, lower = more consistent)")
        print("\nMake sure to run 'python ocr_processor.py' first to generate OCR results.")
        sys.exit(1)
    
    documents = classifier.load_ocr_results(input_file)
    
    classified_documents = classifier.classify_multiple_documents(documents)
    
    output_file = "results/classified_results.json"
    classifier.save_results(classified_documents, output_file)
    
    print("\nClassification complete!")
