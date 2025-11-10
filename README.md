# Document Classification Using Machine Learning# Document Classification Using Machine Learning



A full-stack document management system with automatic classification powered by machine learning. Upload documents, get AI-powered classification suggestions, manage and search your files through a modern web interface.A modular document processing system that performs OCR, classification, and clustering on document images.



## Features## Features



- **🎯 Automatic Classification**: ML-powered document classification on upload- **OCR Text Extraction**: Extract text from images using Tesseract OCR

- **📁 File Management**: Browse, search, and filter uploaded documents- **LLM Classification**: Classify and extract structured data using Google Gemini API

- **✏️ Editable Classifications**: Modify and save document classifications- **Document Clustering**: Group similar documents based on field similarity

- **🔍 Smart Search**: Search by filename or filter by classification type- **Modular Design**: Run each stage independently for fine-tuning

- **🎨 Modern UI**: Responsive React frontend with toggleable sidebar

- **🔧 REST API**: Django REST Framework backend## Installation

- **🗄️ SQLite Database**: Lightweight storage with easy setup

1. Install Python dependencies:

## Tech Stack```bash

pip install -r requirements.txt

### Backend```

- **Django 5.2** - Web framework

- **Django REST Framework** - API layer2. Install Tesseract OCR:

- **SQLite** - Database   - **Windows**: Download from [GitHub Releases](https://github.com/tesseract-ocr/tesseract)

- **Python 3.11+** - Runtime   - **Linux**: `sudo apt-get install tesseract-ocr`

   - **macOS**: `brew install tesseract`

### Frontend

- **React 18** - UI framework3. Set up your Gemini API key:

- **Axios** - HTTP client   - Create a `.env` file in the project root

- **Create React App** - Build tooling   - Add: `GEMINI_API_KEY=your-api-key-here`



### ML/Classification## Project Structure

- **PaddleOCR** - OCR text extraction

- **scikit-learn** - Clustering algorithms```

- **Custom classifier** - Pluggable classification logic├── ocr_processor.py        # Stage 1: OCR text extraction

├── llm_classifier.py       # Stage 2: LLM classification

## Installation├── document_clusterer.py   # Stage 3: Document clustering

├── pipeline.py             # Run all stages together

### Prerequisites├── main.py                 # Original monolithic script (deprecated)

- Python 3.11 or higher├── requirements.txt        # Python dependencies

- Node.js 16 or higher├── .env                    # API keys (create this)

- npm or yarn├── images/                 # Input images directory

├── ocr_results.json        # Stage 1 output

### 1. Clone the Repository├── classified_results.json # Stage 2 output

```bash└── clustering_results.json # Stage 3 output

git clone https://github.com/ashboy27/Document-Classification-using-Machine-Learning.git```

cd Document-Classification-using-Machine-Learning

```## Usage



### 2. Backend Setup### Option 1: Run Complete Pipeline



#### Create Virtual EnvironmentProcess all documents in one go:

```bash```bash

python -m venv .venvpython pipeline.py

```

# Windows

.venv\Scripts\activateWith custom options:

```bash

# macOS/Linuxpython pipeline.py --images my_images --method dbscan --clusters 3

source .venv/bin/activate```

```

### Option 2: Run Stages Independently

#### Install Python Dependencies

```bashThis allows you to fine-tune each stage without re-running previous stages.

pip install -r requirements.txt

```#### Stage 1: OCR Text Extraction

```bash

#### Run Migrations# Process all images in the 'images' folder

```bashpython ocr_processor.py

cd project

python manage.py makemigrations# Process a specific directory

python manage.py migratepython ocr_processor.py path/to/images

```

# Process specific files

#### Start Django Serverpython ocr_processor.py image1.jpg image2.jpg

```bash```

python manage.py runserver

```Output: `ocr_results.json`



The backend will be available at `http://localhost:8000`#### Stage 2: LLM Classification

```bash

### 3. Frontend Setup# Classify documents from ocr_results.json

python llm_classifier.py

Open a new terminal window:

# Classify from a custom file

```bashpython llm_classifier.py my_ocr_results.json

cd frontend```

npm install

npm startOutput: `classified_results.json`

```

#### Stage 3: Document Clustering

The frontend will be available at `http://localhost:3000````bash

# Cluster documents using KMeans (auto-determine clusters)

## Project Structurepython document_clusterer.py



```# Cluster using a custom file

├── project/                    # Django backendpython document_clusterer.py my_classified_results.json

│   ├── backend/               # Main Django app

│   │   ├── models.py         # FileInfo & ClassificationOption models# Cluster using KMeans with 3 clusters

│   │   ├── views.py          # API endpointspython document_clusterer.py classified_results.json kmeans 3

│   │   ├── urls.py           # URL routing

│   │   └── settings.py       # Django configuration# Cluster using DBSCAN

│   ├── manage.pypython document_clusterer.py classified_results.json dbscan

│   └── db.sqlite3            # SQLite database (created after migration)```

├── frontend/                  # React frontend

│   ├── src/Output: `clustering_results.json`

│   │   ├── components/       # Navbar, Sidebar, MyFiles

│   │   ├── App.js           # Main app component## Fine-Tuning Workflow

│   │   ├── FileUpload.js    # Upload with classification

│   │   └── App.css          # Styles### Fine-tune OCR only:

│   ├── package.json1. Adjust Tesseract settings in `ocr_processor.py`

│   └── public/2. Run: `python ocr_processor.py`

├── model/                     # ML classification logic3. Check `ocr_results.json`

│   ├── api/4. If satisfied, proceed: `python llm_classifier.py`

│   │   └── file_classification_api.py

│   └── domain/### Fine-tune Classification only:

│       └── file_classifier.py1. Modify the classification prompt in `llm_classifier.py`

├── user_files/               # Uploaded files storage (auto-created)2. Run: `python llm_classifier.py`

│   └── user_1/              # Per-user folders3. Check `classified_results.json`

├── requirements.txt          # Python dependencies4. If satisfied, proceed: `python document_clusterer.py`

├── .gitignore

└── README.md### Fine-tune Clustering only:

```1. Adjust clustering parameters in `document_clusterer.py`

2. Run: `python document_clusterer.py classified_results.json kmeans 5`

## Usage3. Check `clustering_results.json`



### Uploading Documents## Output Format



1. Navigate to **Upload Documents** in the sidebar### OCR Results (`ocr_results.json`)

2. Select one or multiple files```json

3. Click **Upload**{

4. View the AI-suggested classification for each file  "total_documents": 10,

5. Edit classifications as needed  "documents": [

6. Click **Save** or **Save All**    {

7. You'll be redirected to **My Files** with a success notification      "source_file": "images/doc1.jpg",

      "file_name": "doc1.jpg",

### Managing Files      "extracted_text": "..."

    }

1. Navigate to **My Files** in the sidebar  ]

2. **Search** by filename using the search box}

3. **Filter** by classification type```

4. **Edit** classifications inline

5. **Save** changes### Classification Results (`classified_results.json`)

6. **Delete** files you no longer need```json

{

## API Endpoints  "total_documents": 10,

  "documents": [

### Upload Files    {

```http      "source_file": "images/doc1.jpg",

POST /upload/      "file_name": "doc1.jpg",

Content-Type: multipart/form-data      "extracted_text": "...",

      "classification": {

Response: { uploaded_files: [{ id, file_name, file_path, classification }], options_used: [...] }        "document_type": "ID Card",

```        "extracted_data": {...},

        "field_names_only": [...]

### List Files      }

```http    }

GET /files/?q=search&classification=filter  ]

}

Response: { files: [{ id, file_name, classification, uploaded_at }] }```

```

### Clustering Results (`clustering_results.json`)

### Update Classification```json

```http{

PATCH /files/  "method": "kmeans",

Content-Type: application/json  "n_clusters": 3,

{ "id": 1, "classification": "Invoice" }  "clusters": {

    "Cluster_0": {

Response: { message: "Classification updated", id, classification }      "document_count": 5,

```      "common_fields": [...],

      "documents": [...]

### Delete File    }

```http  }

DELETE /files/}

Content-Type: application/json```

{ "id": 1 }

## Environment Variables

Response: { message: "File deleted", id }

```- `GEMINI_API_KEY`: Your Google Gemini API key (required for classification)



### Get Classification Options## Dependencies

```http

GET /classification-options/- `pytesseract`: OCR wrapper

- `Pillow`: Image processing

Response: { options: ["Driver License", "Passport", "Invoice", "Contract"] }- `google-generativeai`: Gemini API client

```- `scikit-learn`: Machine learning (clustering)

- `python-dotenv`: Environment variable management

## Configuration

## Tips

### Classification Options

1. **For better OCR results**: Use high-quality, high-resolution images

Default classification options are auto-created for user ID 1:2. **For better classification**: Customize the prompt in `llm_classifier.py`

- Driver License3. **For better clustering**: Experiment with different methods and cluster counts

- Passport4. **Save API costs**: Fine-tune OCR first, then run classification once

- Invoice

- Contract## Troubleshooting



You can customize these in the Django admin or via the database.- **Tesseract not found**: Add Tesseract to your system PATH

- **API key error**: Check your `.env` file and GEMINI_API_KEY

### File Storage- **Empty OCR results**: Check image quality and Tesseract installation

- **Clustering error**: Ensure you have at least 2 documents

Files are stored in `user_files/user_{id}/` directories. The structure is:

```## License

user_files/

  └── user_1/MIT License

      ├── document1.pdf
      ├── invoice.jpg
      └── ...
```

### Custom Classification Logic

Edit `model/domain/file_classifier.py` to implement your own classification algorithm. The current implementation randomly selects from provided options as a placeholder.

## Development

### Running Tests
```bash
# Backend
cd project
python manage.py test

# Frontend
cd frontend
npm test
```

### Code Structure

- **Backend**: RESTful API using Django REST Framework
- **Frontend**: React with functional components and hooks
- **State Management**: Local React state (no Redux/Context complexity)
- **Styling**: Custom CSS with CSS variables for theming

## Troubleshooting

### Backend Issues

**"ModuleNotFoundError: No module named 'model'"**
- Ensure `project/backend/settings.py` adds the repo root to `sys.path`
- Check that the virtual environment is activated

**"No such table: backend_fileinfo"**
- Run migrations: `python manage.py makemigrations && python manage.py migrate`

### Frontend Issues

**"Module not found: Can't resolve 'axios'"**
- Install dependencies: `cd frontend && npm install`

**CORS errors**
- Ensure `package.json` has `"proxy": "http://localhost:8000"`
- Restart the React dev server after adding the proxy

**Upload fails silently**
- Check Django server logs for errors
- Verify backend is running on port 8000
- Check browser console for network errors

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

MIT License

## Acknowledgments

- PaddleOCR for OCR capabilities
- Django & Django REST Framework
- React & Create React App community
