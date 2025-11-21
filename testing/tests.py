import os
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
# from model.api.classifier.slm_api import file_classification_slm
from model.api.classifier.hdbscan_api import file_classification_hdbscan
from model.api.classifier.knn_api import file_classification_knn
from model.api.classifier.embeddings_api import file_classification_embeddings
from model.api.classifier.one_class_svm_api import file_classification_one_class_svm
from model.api.classifier.isolation_forest_api import file_classification_isolation_forest
from datetime import datetime
data_path_from_root = r"data\id_cards"

EXCEL_FILE = r"testing\data_info.xlsx"
LOG_FILE = r"testing\logs.txt"

def get_options():
    return ["CNIC", "Driver's License"]
def log_results(log_message):
    with open(LOG_FILE, "a") as log_file:
        log_file.write(log_message + "\n")

def process_file(df, classification_function, api_name, options=None):
    """Generic function to process files and evaluate classifications."""
    y_true = []
    y_pred = []

    for _, row in df.iterrows():
        file_name = row["File_name"]
        expected_classification = row["Classification"]

        file_path = os.path.join(data_path_from_root, file_name)

        if not os.path.exists(file_path):
            log_results(f"File not found: {file_name}")
            continue

        try:
            classification_result = classification_function(file_path, options=options or [])
            y_true.append(expected_classification)
            y_pred.append(classification_result)
        except Exception as e:
            log_results(f"Error processing file {file_name}: {str(e)}")

    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, average="weighted", zero_division=0)
    recall = recall_score(y_true, y_pred, average="weighted", zero_division=0)
    f1 = f1_score(y_true, y_pred, average="weighted", zero_division=0)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_results(f"{timestamp} | API: {api_name} | Accuracy: {accuracy:.4f} | Precision: {precision:.4f} | Recall: {recall:.4f} | F1 Score: {f1:.4f}")

def slm_method(df):
    """Process files and evaluate classifications using SLM."""
    # process_file(df, file_classification_slm, "SLM", options=get_options())

def hdbscan_method(df):
    """Process files and evaluate classifications using HDBSCAN."""
    process_file(df, file_classification_hdbscan, "HDBSCAN", options=get_options())

def knn_method(df):
    """Process files and evaluate classifications using KNN."""
    process_file(df, file_classification_knn, "KNN", options=get_options())
    
def embeddings_method(df):
    """Process files and evaluate classifications using Embeddings."""
    process_file(df, file_classification_embeddings, "Embeddings", options=get_options())

def OneClassSvm_method(df):
    """Process files and evaluate classifications using One-Class SVM."""
    process_file(df, file_classification_one_class_svm, "One-Class SVM", options= get_options())

def IsolationForest_method(df):
    """Process files and evaluate classifications using Isolation Forest."""
    process_file(df, file_classification_isolation_forest, "Isolation Forest", options= get_options())

def evaluate_file_classification():
    df = pd.read_excel(EXCEL_FILE)

    if not {"File_name", "Classification"}.issubset(df.columns):
        raise ValueError("The Excel file must contain 'File_name' and 'Classification' columns.")

    # slm_method(df)
    hdbscan_method(df)
    knn_method(df)
    embeddings_method(df)
    OneClassSvm_method(df)
    IsolationForest_method(df)

if __name__ == "__main__":
    evaluate_file_classification()