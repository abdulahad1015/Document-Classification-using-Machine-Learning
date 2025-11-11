import os
from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

import os
import sys

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)
from initial_work.ocr_processor import OCRProcessor



def classify_document(document_data: str, categories: list) -> str:

    llm = 
    system_prompt = """
    You are an expert document classifier.
    You will be given details about a document type extracted via OCR.
    You have to classify the document into one of the provided categories based on its content.
    First, understand each category and its characteristics. Then, analyze the document data to identify key features that match those characteristics.
    Finally, assign the document to the most appropriate category.
    If the document does not fit any category, respond with 'none'.
    """

    human_prompt = f"""
    Document: {document_data}
    Categories:{categories}

    Classify the document into one of the categories listed above.
    Provide only the category name as your response.
    If it does not fit any category, respond with 'none'.

    """

    prompt = ChatPromptTemplate(
        [("system", {"system_prompt"}), ("human", {"human_prompt"})]
    )

    result = prompt | llm | StrOutputParser()

    return result

def fileclassfy(file_path: str, options) -> str:
    if not options:
        raise ValueError("options must be a non-empty list")

    processor = OCRProcessor()
    ocr_result = processor.process_single_document(file_path)

    


if __name__ == "__main__":


    file_path = r"D:\Desktop\FYP\data\id_cards\121613462_3957348240946268_3140575577819881892_n.jpg"

    if not Path(file_path).exists():
        print(f"File not found: {file_path}")
    else:
        fileclassfy(file_path, options=["ocr"])
