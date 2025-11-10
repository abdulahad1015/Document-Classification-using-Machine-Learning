"""
Document Clustering Module
Handles clustering of classified documents based on field similarity.
"""
import os
import json
from typing import Dict, Any, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans, DBSCAN
from collections import defaultdict


class DocumentClusterer:
    def __init__(self):
        """Initialize the document clusterer."""
        self.documents = []
    
    def load_classified_documents(self, input_path: str) -> List[Dict[str, Any]]:
        """Load classified documents from a JSON file."""
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.documents = data['documents']
        print(f"Loaded {data['total_documents']} classified documents from {input_path}")
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
            raise ValueError("No documents to cluster. Load documents first using load_classified_documents().")
        
        if len(self.documents) < 2:
            print(f"Warning: Only {len(self.documents)} document(s) found. Clustering requires at least 2 documents.")
            print("Skipping clustering and returning individual document results.")
            
            results = {
                "method": method,
                "n_clusters": 0,
                "clusters": {
                    "Cluster_0": {
                        "document_count": len(self.documents),
                        "common_fields": [],
                        "all_unique_fields": [],
                        "documents": []
                    }
                },
                "vectorizer_features": []
            }
            
            for doc in self.documents:
                field_names = doc["classification"].get("field_names_only", [])
                if not field_names:
                    field_names = list(doc["classification"].get("extracted_data", {}).keys())
                
                results["clusters"]["Cluster_0"]["documents"].append({
                    "file_name": doc["file_name"],
                    "file_path": doc["source_file"],
                    "document_type": doc["classification"].get("document_type", "unknown"),
                    "field_names": field_names,
                    "extracted_data": doc["classification"].get("extracted_data", {})
                })
                
                results["clusters"]["Cluster_0"]["all_unique_fields"] = list(set(field_names))
                results["clusters"]["Cluster_0"]["common_fields"] = field_names
            
            return results
        
        field_texts = []
        for doc in self.documents:
            field_names = doc["classification"].get("field_names_only", [])
            if not field_names:
                field_names = list(doc["classification"].get("extracted_data", {}).keys())
            
            field_str = " ".join(field_names)
            field_texts.append(field_str)
        
        vectorizer = TfidfVectorizer(lowercase=True, token_pattern=r'\b\w+\b')
        X = vectorizer.fit_transform(field_texts)
        
        if method == "kmeans":
            if n_clusters is None:
                n_clusters = min(5, max(2, len(self.documents) // 3))
            
            n_clusters = min(n_clusters, len(self.documents))
            
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            labels = kmeans.fit_predict(X)
            
        elif method == "dbscan":
            dbscan = DBSCAN(eps=0.5, min_samples=2, metric='cosine')
            labels = dbscan.fit_predict(X.toarray())
        else:
            raise ValueError(f"Unknown method: {method}")
        
        clusters = defaultdict(list)
        for idx, label in enumerate(labels):
            cluster_label = f"Cluster_{label}" if label >= 0 else "Noise"
            
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
        
        cluster_info = {}
        for cluster_label, docs in clusters.items():
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
    
    def save_results(self, results: Dict[str, Any], output_path: str):
        """Save clustering results to a JSON file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nClustering results saved to: {output_path}")


if __name__ == "__main__":
    import sys
    
    clusterer = DocumentClusterer()
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = "results/classified_results.json"
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        print("Usage: python document_clusterer.py [classified_results.json]")
        print("\nMake sure to run 'python llm_classifier.py' first to generate classified results.")
        sys.exit(1)
    
    clusterer.load_classified_documents(input_file)
    
    method = "kmeans"  
    n_clusters = None  
    
    if len(sys.argv) > 2:
        method = sys.argv[2]
    if len(sys.argv) > 3:
        try:
            n_clusters = int(sys.argv[3])
        except ValueError:
            print(f"Warning: Invalid n_clusters value '{sys.argv[3]}', using auto-determination")
    
    print(f"\nClustering documents using {method.upper()}...")
    clustering_results = clusterer.cluster_by_field_similarity(
        n_clusters=n_clusters,
        method=method
    )
    
    clusterer.print_cluster_summary(clustering_results)
    
    output_file = "clustering_results.json"
    clusterer.save_results(clustering_results, output_file)
    
    print("\nClustering complete!")
    print(f"Results saved to {output_file}")
