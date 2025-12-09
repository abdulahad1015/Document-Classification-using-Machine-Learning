from model.domain.ocr.extraction import extract

def get_extraction(file_path: str) -> str:
    return extract(file_path = file_path)