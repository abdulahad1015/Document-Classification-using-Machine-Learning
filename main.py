"""
Pipeline Script - Run all stages together
This script runs OCR, classification, and clustering in sequence.
"""
import os
import sys
from ocr_processor import OCRProcessor
from llm_classifier import LLMClassifier
from document_clusterer import DocumentClusterer
from time import time


def run_full_pipeline(image_dir: str = "images", 
                     ocr_output: str = "results/ocr_results.json",
                     classified_output: str = "results/classified_results.json",
                     clustering_output: str = "results/clustering_results.json",
                     clustering_method: str = "kmeans",
                     n_clusters: int = None):
    """
    Run the complete document processing pipeline.
    
    Args:
        image_dir: Directory containing images to process
        ocr_output: Path to save OCR results
        classified_output: Path to save classification results
        clustering_output: Path to save clustering results
        clustering_method: 'kmeans' or 'dbscan'
        n_clusters: Number of clusters for KMeans (None for auto)
    """
    print("="*70)
    print("DOCUMENT PROCESSING PIPELINE")
    print("="*70)
    
    if not os.path.exists(image_dir):
        print(f"Error: Image directory '{image_dir}' not found.")
        sys.exit(1)
    
    image_paths = [
        os.path.join(image_dir, f) 
        for f in os.listdir(image_dir) 
        if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff'))
    ]
    
    if not image_paths:
        print(f"Error: No image files found in '{image_dir}'")
        sys.exit(1)
    
    print(f"\nFound {len(image_paths)} images to process")
    
    print("\n" + "="*70)
    print("STAGE 1: OCR TEXT EXTRACTION")
    print("="*70)
    
    ocr_processor = OCRProcessor()
    ocr_results = ocr_processor.process_multiple_documents(image_paths)
    ocr_processor.save_results(ocr_results, ocr_output)
    
    print("\n" + "="*70)
    print("STAGE 2: LLM CLASSIFICATION")
    print("="*70)
    
    try:
        classifier = LLMClassifier()
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set GEMINI_API_KEY in .env file or environment variable")
        sys.exit(1)
    
    classified_documents = classifier.classify_multiple_documents(ocr_results)
    classifier.save_results(classified_documents, classified_output)
    
    print("\n" + "="*70)
    print("STAGE 3: DOCUMENT CLUSTERING")
    print("="*70)
    
    clusterer = DocumentClusterer()
    clusterer.documents = classified_documents
    
    clustering_results = clusterer.cluster_by_field_similarity(
        n_clusters=n_clusters,
        method=clustering_method
    )
    
    clusterer.print_cluster_summary(clustering_results)
    clusterer.save_results(clustering_results, clustering_output)
    
    print("\n" + "="*70)
    print("PIPELINE COMPLETE!")
    print("="*70)
    print(f"OCR Results: {ocr_output}")
    print(f"Classification Results: {classified_output}")
    print(f"Clustering Results: {clustering_output}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run the complete document processing pipeline")
    parser.add_argument("--images", default="images", help="Directory containing images (default: images)")
    parser.add_argument("--method", default="kmeans", choices=["kmeans", "dbscan"], 
                       help="Clustering method (default: kmeans)")
    parser.add_argument("--clusters", type=int, default=None, 
                       help="Number of clusters for KMeans (default: auto-determine)")
    
    args = parser.parse_args()
    start = time()
    run_full_pipeline(
        image_dir=args.images,
        clustering_method=args.method,
        n_clusters=args.clusters
    )
    print("Execution time: %.2f seconds" % (time() - start))
