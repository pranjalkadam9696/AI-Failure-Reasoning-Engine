import json
import re


# Load the failure knowledge base
with open("failure_database.json", "r") as file:
    failure_data = json.load(file)


# Failure keywords and related phrases
failure_keywords = {
    "overfitting": [
        "overfitting",
        "memorizing training data",
        "model is memorizing",
        "training accuracy is high",
        "training accuracy high",
        "test accuracy is low",
        "testing accuracy is low",
        "validation accuracy is low",
        "works well on training data",
        "fails on unseen data",
        "poor performance on test data"
    ],

    "underfitting": [
        "underfitting",
        "model is too simple",
        "model too simple",
        "training accuracy is low",
        "training accuracy low",
        "poor training performance",
        "cannot learn the pattern"
    ],

    "low_accuracy": [
        "low accuracy",
        "accuracy is low",
        "poor accuracy",
        "bad accuracy",
        "accuracy is poor",
        "model accuracy is poor"
    ],

    "data_imbalance": [
        "data imbalance",
        "imbalanced data",
        "class imbalance",
        "unbalanced dataset",
        "classes are imbalanced",
        "unequal classes"
    ],

    "missing_values": [
        "missing values",
        "missing data",
        "null values",
        "empty values",
        "some values are missing",
        "data is missing"
    ],

    "outliers": [
        "outliers",
        "outlier",
        "unusual values",
        "extreme values",
        "abnormal values",
        "very different values"
    ],

    "data_leakage": [
        "data leakage",
        "information leakage",
        "test data in training",
        "test information in training",
        "future information in training"
    ],

    "wrong_prediction": [
        "wrong prediction",
        "incorrect prediction",
        "wrong output",
        "incorrect output",
        "model predicts incorrectly",
        "model is predicting wrong"
    ],

    "high_training_time": [
        "training time is high",
        "high training time",
        "training takes too long",
        "training is slow",
        "slow training",
        "model takes too long to train"
    ],

    "model_bias": [
        "model bias",
        "biased model",
        "unfair prediction",
        "unfair predictions",
        "model is unfair",
        "biased prediction"
    ]
}


def clean_text(text):
    """
    Clean and normalize user input.
    """
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def detect_failure(user_input):
    """
    Detect the most likely AI/ML failure.
    """

    user_input = clean_text(user_input)

    scores = {}

    # Special rule for overfitting
    if (
        "training accuracy" in user_input
        and "testing accuracy" in user_input
        and "high" in user_input
        and "low" in user_input
    ):
        return "overfitting", 95

    # Check keywords for every failure
    for failure, keywords in failure_keywords.items():

        score = 0

        for keyword in keywords:

            keyword = clean_text(keyword)

            if keyword in user_input:
                score += 1

        if score > 0:
            scores[failure] = score

    # If no failure is detected
    if not scores:
        return None, 0

    # Select the failure with the highest score
    best_failure = max(scores, key=scores.get)

    # Calculate confidence
    confidence = min(60 + (scores[best_failure] - 1) * 15, 95)

    return best_failure, confidence


def generate_evidence(user_input, failure):
    """
    Generate evidence from the user's problem description.
    """

    user_input = clean_text(user_input)

    evidence = []

    if failure == "overfitting":

        if "training accuracy" in user_input:
            evidence.append("Training accuracy information was found.")

        if "testing accuracy" in user_input:
            evidence.append("Testing accuracy information was found.")

        if "memorizing training data" in user_input:
            evidence.append("The model appears to be memorizing training data.")

        if "unseen data" in user_input:
            evidence.append("The model has difficulty with unseen data.")

        if "poor performance on test data" in user_input:
            evidence.append("The model performs poorly on test data.")

    elif failure == "underfitting":

        if "model too simple" in user_input:
            evidence.append("The model is described as too simple.")

        if "training accuracy" in user_input:
            evidence.append("Low training performance was mentioned.")

        if "cannot learn the pattern" in user_input:
            evidence.append("The model cannot learn important patterns.")

    elif failure == "low_accuracy":

        evidence.append("The input indicates low model accuracy.")

    elif failure == "data_imbalance":

        evidence.append("The input indicates an imbalance between classes.")

    elif failure == "missing_values":

        evidence.append("Missing or null values were mentioned in the dataset.")

    elif failure == "outliers":

        evidence.append("Unusual or extreme values were found in the dataset.")

    elif failure == "data_leakage":

        evidence.append("Training data may contain test or future information.")

    elif failure == "wrong_prediction":

        evidence.append("The model is producing incorrect predictions.")

    elif failure == "high_training_time":

        evidence.append("The model requires a long time to complete training.")

    elif failure == "model_bias":

        evidence.append("The model may be producing biased or unfair predictions.")

    if not evidence:
        evidence.append("The failure was identified from the problem description.")

    return evidence


def generate_reasoning(failure):
    """
    Generate an explanation for the detected failure.
    """

    reasoning = {

        "overfitting":
            "The model may have learned the training data too closely, causing poor performance on new or unseen data.",

        "underfitting":
            "The model may be too simple to learn the important patterns in the training data.",

        "low_accuracy":
            "The model is not producing enough correct predictions, which may indicate problems with data, features, or model selection.",

        "data_imbalance":
            "Unequal class distribution can cause the model to favor the majority class.",

        "missing_values":
            "Missing values can reduce data quality and negatively affect model training.",

        "outliers":
            "Extreme values can influence model learning and may produce unreliable predictions.",

        "data_leakage":
            "Using test or future information during training can produce unrealistically high model performance.",

        "wrong_prediction":
            "Incorrect predictions may be caused by poor data quality, unsuitable features, or model limitations.",

        "high_training_time":
            "Long training time may be caused by a large dataset, a complex model, or limited computing resources.",

        "model_bias":
            "Biased training data can cause the model to produce unfair predictions."
    }

    return reasoning.get(
        failure,
        "The system identified a possible AI/ML failure from the provided information."
    )


def analyze_failure(user_input):

    failure, confidence = detect_failure(user_input)

    if failure is None:

        print("\n===================================")
        print("AI FAILURE REASONING ENGINE")
        print("===================================")

        print("\nFailure could not be identified.")

        print("\nPlease describe the problem in more detail.")

        print("\nExample:")
        print("My training accuracy is high but testing accuracy is low.")

        print("\n===================================")

        return

    information = failure_data[failure]

    evidence = generate_evidence(user_input, failure)

    reasoning = generate_reasoning(failure)

    print("\n===================================")
    print("AI FAILURE REASONING ENGINE")
    print("===================================")

    print("\nFailure Type:")
    print(failure.replace("_", " ").title())

    print("\nConfidence:")
    print(str(confidence) + "%")

    print("\nEvidence:")

    for item in evidence:
        print("- " + item)

    print("\nReasoning:")
    print(reasoning)

    print("\nDescription:")
    print(information["description"])

    print("\nPossible Causes:")

    for cause in information["causes"]:
        print("- " + cause)

    print("\nRecommended Solutions:")

    for solution in information["solutions"]:
        print("- " + solution)

    print("\n===================================")


if __name__ == "__main__":
    user_input = input("\nDescribe your AI/ML problem: ")
    analyze_failure(user_input)
    

