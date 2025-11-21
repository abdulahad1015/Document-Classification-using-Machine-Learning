from model.domain.classifier.isolation_forest import fileclassfy_isolation_forest

def file_classification_isolation_forest(file_path: str, options: list) -> str:
    """
    Classify the file at the given path using the fileclassfy_isolation_forest function.

    Args:
        file_path (str): The path to the file to be classified.
        options (list): A list of options to pass to the classifier.

    Returns:
        str: The classification result.
    """
    classification_result = fileclassfy_isolation_forest(file_path, options)
    return classification_result