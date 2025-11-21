import os
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from model.api.classifier.slm_api import file_classification

data_path_from_root = r"data\id_cards"

EXCEL_FILE = r"testing\data_info.xlsx"
LOG_FILE = "logs.txt"

def log_results(log_message):
    with open(LOG_FILE, "a") as log_file:
        log_file.write(log_message + "\n")

def slm_method(df):
    """Process files and evaluate classifications using SLM."""
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
            classification_result = file_classification(file_path, options=[])
            y_true.append(expected_classification)
            y_pred.append(classification_result)
        except Exception as e:
            log_results(f"Error processing file {file_name}: {str(e)}")

    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, average="weighted", zero_division=0)
    recall = recall_score(y_true, y_pred, average="weighted", zero_division=0)
    f1 = f1_score(y_true, y_pred, average="weighted", zero_division=0)

    log_results("API: file_classification (SLM)")
    log_results(f"Accuracy: {accuracy:.4f}")
    log_results(f"Precision: {precision:.4f}")
    log_results(f"Recall: {recall:.4f}")
    log_results(f"F1 Score: {f1:.4f}")

def evaluate_file_classification():
    df = pd.read_excel(EXCEL_FILE)

    if not {"File_name", "Classification"}.issubset(df.columns):
        raise ValueError("The Excel file must contain 'File_name' and 'Classification' columns.")

    slm_method(df)

if __name__ == "__main__":
    evaluate_file_classification()