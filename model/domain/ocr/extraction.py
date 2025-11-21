import os
import sys


from initial_work.ocr_processor import OCRProcessor


def extract(file_path: str) -> str:

    processor = OCRProcessor()
    ocr_result = processor.process_single_document(file_path)
    return ocr_result