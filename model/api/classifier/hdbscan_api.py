from model.domain.classifier.hdbscan import fileclassfy_hdbscan


def file_classification_hdbscan(file_path: str, options: list) -> str:
    """
    Classify the file at the given path using the fileclassfy_hdbscan function.

    Args:
        file_path (str): The path to the file to be classified.
        options (list): A list of options to pass to the classifier.

    Returns:
        str: The classification result.
    """
    classification_result = fileclassfy_hdbscan(file_path, options)
    return classification_result