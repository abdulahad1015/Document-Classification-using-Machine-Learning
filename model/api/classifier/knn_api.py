from model.domain.classifier.knn import fileclassfy_knn


def file_classification_knn(file_path: str, options: list) -> str:
    """
    Classify the file at the given path using the fileclassfy_knn function.

    Args:
        file_path (str): The path to the file to be classified.
        options (list): A list of options to pass to the classifier.

    Returns:
        str: The classification result.
    """
    classification_result = fileclassfy_knn(file_path, options)
    return classification_result