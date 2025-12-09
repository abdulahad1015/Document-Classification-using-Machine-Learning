# from model.api.ocr.extraction_api import get_extraction

def classify_document(document_data: str, categories: list) -> str:
    return "CNIC"


def fileclassfy_hdbscan(file_path: str, options) -> str:
    if not options:
        raise ValueError("options must be a non-empty list")

    # ocr_result = get_extraction(file_path)
    ocr_result = ""
    classification = classify_document(ocr_result, options)
    return classification