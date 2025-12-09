import os
from ocr_processor import OCRProcessor
from llm_classifier import LLMClassifier

def process_single_image(image_path: str):

    if not os.path.exists(image_path):
        print(f"Error: Image file '{image_path}' not found.")
        return
    ocr_processor = OCRProcessor()
    ocr_result = ocr_processor.process_single_document(image_path)
    
    try:
        classifier = LLMClassifier()
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set GEMINI_API_KEY in .env file or environment variable")
        return
    
    classified_document = classifier.classify_document(ocr_result)
    return classified_document
    

if __name__ == "__main__":
    print(process_single_image("images/id1.jpg"))
