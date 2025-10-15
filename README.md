# Document Classification Using Machine Learning

A modular document processing system that performs OCR, classification, and clustering on document images.

## Features

- **OCR Text Extraction**: Extract text from images using Tesseract OCR
- **LLM Classification**: Classify and extract structured data using Google Gemini API
- **Document Clustering**: Group similar documents based on field similarity
- **Modular Design**: Run each stage independently for fine-tuning

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install Tesseract OCR:
   - **Windows**: Download from [GitHub Releases](https://github.com/tesseract-ocr/tesseract)
   - **Linux**: `sudo apt-get install tesseract-ocr`
   - **macOS**: `brew install tesseract`

3. Set up your Gemini API key:
   - Create a `.env` file in the project root
   - Add: `GEMINI_API_KEY=your-api-key-here`

## Project Structure

```
├── ocr_processor.py        # Stage 1: OCR text extraction
├── llm_classifier.py       # Stage 2: LLM classification
├── document_clusterer.py   # Stage 3: Document clustering
├── pipeline.py             # Run all stages together
├── main.py                 # Original monolithic script (deprecated)
├── requirements.txt        # Python dependencies
├── .env                    # API keys (create this)
├── images/                 # Input images directory
├── ocr_results.json        # Stage 1 output
├── classified_results.json # Stage 2 output
└── clustering_results.json # Stage 3 output
```

## Usage

### Option 1: Run Complete Pipeline

Process all documents in one go:
```bash
python pipeline.py
```

With custom options:
```bash
python pipeline.py --images my_images --method dbscan --clusters 3
```

### Option 2: Run Stages Independently

This allows you to fine-tune each stage without re-running previous stages.

#### Stage 1: OCR Text Extraction
```bash
# Process all images in the 'images' folder
python ocr_processor.py

# Process a specific directory
python ocr_processor.py path/to/images

# Process specific files
python ocr_processor.py image1.jpg image2.jpg
```

Output: `ocr_results.json`

#### Stage 2: LLM Classification
```bash
# Classify documents from ocr_results.json
python llm_classifier.py

# Classify from a custom file
python llm_classifier.py my_ocr_results.json
```

Output: `classified_results.json`

#### Stage 3: Document Clustering
```bash
# Cluster documents using KMeans (auto-determine clusters)
python document_clusterer.py

# Cluster using a custom file
python document_clusterer.py my_classified_results.json

# Cluster using KMeans with 3 clusters
python document_clusterer.py classified_results.json kmeans 3

# Cluster using DBSCAN
python document_clusterer.py classified_results.json dbscan
```

Output: `clustering_results.json`

## Fine-Tuning Workflow

### Fine-tune OCR only:
1. Adjust Tesseract settings in `ocr_processor.py`
2. Run: `python ocr_processor.py`
3. Check `ocr_results.json`
4. If satisfied, proceed: `python llm_classifier.py`

### Fine-tune Classification only:
1. Modify the classification prompt in `llm_classifier.py`
2. Run: `python llm_classifier.py`
3. Check `classified_results.json`
4. If satisfied, proceed: `python document_clusterer.py`

### Fine-tune Clustering only:
1. Adjust clustering parameters in `document_clusterer.py`
2. Run: `python document_clusterer.py classified_results.json kmeans 5`
3. Check `clustering_results.json`

## Output Format

### OCR Results (`ocr_results.json`)
```json
{
  "total_documents": 10,
  "documents": [
    {
      "source_file": "images/doc1.jpg",
      "file_name": "doc1.jpg",
      "extracted_text": "..."
    }
  ]
}
```

### Classification Results (`classified_results.json`)
```json
{
  "total_documents": 10,
  "documents": [
    {
      "source_file": "images/doc1.jpg",
      "file_name": "doc1.jpg",
      "extracted_text": "...",
      "classification": {
        "document_type": "ID Card",
        "extracted_data": {...},
        "field_names_only": [...]
      }
    }
  ]
}
```

### Clustering Results (`clustering_results.json`)
```json
{
  "method": "kmeans",
  "n_clusters": 3,
  "clusters": {
    "Cluster_0": {
      "document_count": 5,
      "common_fields": [...],
      "documents": [...]
    }
  }
}
```

## Environment Variables

- `GEMINI_API_KEY`: Your Google Gemini API key (required for classification)

## Dependencies

- `pytesseract`: OCR wrapper
- `Pillow`: Image processing
- `google-generativeai`: Gemini API client
- `scikit-learn`: Machine learning (clustering)
- `python-dotenv`: Environment variable management

## Tips

1. **For better OCR results**: Use high-quality, high-resolution images
2. **For better classification**: Customize the prompt in `llm_classifier.py`
3. **For better clustering**: Experiment with different methods and cluster counts
4. **Save API costs**: Fine-tune OCR first, then run classification once

## Troubleshooting

- **Tesseract not found**: Add Tesseract to your system PATH
- **API key error**: Check your `.env` file and GEMINI_API_KEY
- **Empty OCR results**: Check image quality and Tesseract installation
- **Clustering error**: Ensure you have at least 2 documents

## License

MIT License
