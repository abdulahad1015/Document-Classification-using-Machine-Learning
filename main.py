import os
from dotenv import load_dotenv
import json
from pathlib import Path
from typing import Dict, Any, List
import pytesseract
from PIL import Image
import google.generativeai as genai
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans, DBSCAN
import numpy as np
from collections import defaultdict

class DocumentProcessor:
    def __init__(self, gemini_api_key: str = None):
        # Load environment variables from .env file if present
        load_dotenv()
        """
        Initialize the document processor with OCR and Gemini LLM capabilities.
        
        Args:
            gemini_api_key: API key for Google Gemini (or set GEMINI_API_KEY env var)
        """
        self.api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key required")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("models/gemini-2.0-flash-exp")
        self.documents = []
    
    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extract text from an image using Tesseract OCR.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Extracted text as string
        """
        try:
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img)
            print(text)
            return text.strip()
        except Exception as e:
            raise Exception(f"OCR extraction failed: {str(e)}")
    
    def classify_with_llm(self, text: str, classification_prompt: str = None) -> Dict[str, Any]:
        """
        Send extracted text to Gemini LLM for classification and structured extraction.
        
        Args:
            text: The extracted text to classify
            classification_prompt: Custom prompt for classification (optional)
        Returns:
            Dictionary containing the classified data in JSON format
        """
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
        
        prompt = f"{classification_prompt}\n\n{text}\n\nProvide response in valid JSON format only."
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
            # Extract JSON from response (handles cases where LLM adds extra text)
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
            else:
                return json.loads(response_text)
        except json.JSONDecodeError as e:
            return {
                "error": "Failed to parse JSON response",
                "raw_response": response_text,
                "details": str(e)
            }
        except Exception as e:
            raise Exception(f"LLM classification failed: {str(e)}")
    
    def process_document(self, image_path: str, classification_prompt: str = None) -> Dict[str, Any]:
        """
        Complete workflow: OCR extraction + LLM classification.
        
        Args:
            image_path: Path to the document image
            classification_prompt: Custom classification prompt (optional)
            
        Returns:
            Dictionary with extracted text and classification results
        """
        print(f"Processing document: {image_path}")
        
        # Step 1: Extract text using OCR
        print("Step 1: Extracting text with OCR...")
        extracted_text = self.extract_text_from_image(image_path)
        print(f"Extracted {len(extracted_text)} characters")
        
        # Step 2: Classify with LLM
        print("Step 2: Classifying with LLM...")
        classification = self.classify_with_llm(extracted_text, classification_prompt)
        
        # Combine results
        result = {
            "source_file": image_path,
            "file_name": Path(image_path).name,
            "extracted_text": extracted_text,
            "classification": classification
        }
        
        print("Processing complete!")
        return result
    
    def process_multiple_documents(self, image_paths: List[str], classification_prompt: str = None) -> List[Dict[str, Any]]:
        """
        Process multiple documents and store results for clustering.
        
        Args:
            image_paths: List of paths to document images
            classification_prompt: Custom classification prompt (optional)
            
        Returns:
            List of processed document results
        """
        self.documents = []
        
        for path in image_paths:
            try:
                result = self.process_document(path, classification_prompt)
                self.documents.append(result)
            except Exception as e:
                print(f"Error processing {path}: {str(e)}")
                continue
        
        print(f"\nSuccessfully processed {len(self.documents)} documents")
        return self.documents
    
    def cluster_by_field_similarity(self, n_clusters: int = None, method: str = "kmeans") -> Dict[str, Any]:
        """
        Cluster documents based on field name similarity.
        
        Args:
            n_clusters: Number of clusters (for KMeans). If None, auto-determines
            method: 'kmeans' or 'dbscan'
            
        Returns:
            Dictionary with clustering results
        """
        if not self.documents:
            raise ValueError("No documents to cluster. Process documents first using process_multiple_documents().")
        
        # Create field name strings for each document
        field_texts = []
        for doc in self.documents:
            # Extract field names from classification
            field_names = doc["classification"].get("field_names_only", [])
            if not field_names:
                # Fallback: use keys from extracted_data if field_names_only not present
                field_names = list(doc["classification"].get("extracted_data", {}).keys())
            
            field_str = " ".join(field_names)
            field_texts.append(field_str)
        
        # Vectorize field names using TF-IDF
        vectorizer = TfidfVectorizer(lowercase=True, token_pattern=r'\b\w+\b')
        X = vectorizer.fit_transform(field_texts)
        
        # Cluster based on method
        if method == "kmeans":
            if n_clusters is None:
                # Auto-determine optimal clusters (simple heuristic)
                n_clusters = min(5, max(2, len(self.documents) // 3))
            
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            labels = kmeans.fit_predict(X)
            
        elif method == "dbscan":
            # DBSCAN auto-determines number of clusters
            dbscan = DBSCAN(eps=0.5, min_samples=2, metric='cosine')
            labels = dbscan.fit_predict(X.toarray())
        else:
            raise ValueError(f"Unknown method: {method}")
        
        # Organize results by cluster
        clusters = defaultdict(list)
        for idx, label in enumerate(labels):
            cluster_label = f"Cluster_{label}" if label >= 0 else "Noise"
            
            # Get field names for this document
            field_names = self.documents[idx]["classification"].get("field_names_only", [])
            if not field_names:
                field_names = list(self.documents[idx]["classification"].get("extracted_data", {}).keys())
            
            clusters[cluster_label].append({
                "file_name": self.documents[idx]["file_name"],
                "file_path": self.documents[idx]["source_file"],
                "document_type": self.documents[idx]["classification"].get("document_type", "unknown"),
                "field_names": field_names,
                "extracted_data": self.documents[idx]["classification"].get("extracted_data", {})
            })
        
        # Calculate cluster characteristics
        cluster_info = {}
        for cluster_label, docs in clusters.items():
            # Find common fields across cluster
            all_fields = [set(doc["field_names"]) for doc in docs]
            common_fields = set.intersection(*all_fields) if all_fields else set()
            
            cluster_info[cluster_label] = {
                "document_count": len(docs),
                "common_fields": list(common_fields),
                "all_unique_fields": list(set().union(*all_fields)) if all_fields else [],
                "documents": docs
            }
        
        results = {
            "method": method,
            "n_clusters": len([k for k in clusters.keys() if k != "Noise"]),
            "clusters": cluster_info,
            "vectorizer_features": vectorizer.get_feature_names_out().tolist()
        }
        
        return results
    
    def print_cluster_summary(self, results: Dict[str, Any]):
        """Print a readable summary of clustering results."""
        print("\n" + "="*70)
        print(f"CLUSTERING SUMMARY ({results['method'].upper()})")
        print("="*70)
        print(f"Total clusters found: {results['n_clusters']}")
        
        for cluster_label, info in results['clusters'].items():
            print(f"\n{cluster_label}:")
            print(f"  Documents: {info['document_count']}")
            print(f"  Common fields: {', '.join(info['common_fields']) if info['common_fields'] else 'None'}")
            
            doc_types = set(d['document_type'] for d in info['documents'])
            print(f"  Document types: {', '.join(doc_types)}")
            print(f"  Files:")
            for doc in info['documents']:
                print(f"    - {doc['file_name']}")
    
    def save_results(self, result: Dict[str, Any], output_path: str):
        """Save results to a JSON file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Results saved to: {output_path}")


# Example usage
if __name__ == "__main__":
    # Initialize processor
    processor = DocumentProcessor()

    # Process multiple documents and cluster them
    print("\n\n" + "="*70)
    print("MULTIPLE DOCUMENT PROCESSING WITH CLUSTERING")
    print("="*70)
    
    # List of document images to process
    image_paths = [
        "images/img1.jpg",
        "images/img2.jpg",
        "images/img3.jpg",
        "images/img4.jpg",
        "images/img5.jpg",
        "images/img6.jpg",

    ]
    
    # Process all documents
    print("\nStep 1: Processing multiple documents...")
    documents = processor.process_multiple_documents(image_paths)
    
    # Cluster by field similarity
    print("\nStep 2: Clustering documents by field similarity...")
    clustering_results = processor.cluster_by_field_similarity(
        n_clusters=None,  # Auto-determine or specify a number
        method="kmeans"   # or "dbscan"
    )
    
    # Display clustering results
    processor.print_cluster_summary(clustering_results)
    
    # Save clustering results
    processor.save_results(clustering_results, "clustering_results.json")