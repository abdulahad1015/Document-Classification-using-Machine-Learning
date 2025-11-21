import os
import csv
from paddleocr import PaddleOCR

INPUT_DIR = "documents/"
OUTPUT_CSV = "ocr_output.csv"
LANG = "en"

ocr = PaddleOCR(use_angle_cls=True, lang=LANG, show_log=False)

VALID_EXT = [".png", ".jpg", ".jpeg", ".bmp", ".pdf"]

def extract_text(file_path):
    result = ocr.ocr(file_path, cls=True)
    text_chunks = []
    for page in result:
        for line in page:
            text = line[1][0]
            text_chunks.append(text)
    return "\n".join(text_chunks)

def main():
    files = [f for f in os.listdir(INPUT_DIR)
             if os.path.splitext(f)[1].lower() in VALID_EXT]

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["filename", "extracted_text"])
        for filename in files:
            full_path = os.path.join(INPUT_DIR, filename)
            text = extract_text(full_path)
            writer.writerow([filename, text])

    print("OCR extraction complete!")
    print(f"CSV saved as: {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
