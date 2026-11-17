
from flask import Flask, render_template, request, redirect, url_for
import json
import os

from reasoning_engine import (
    detect_failure,
    generate_evidence,
    generate_reasoning,
    failure_data
)

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(BASE_DIR, "history.json")


# -------------------- HISTORY FUNCTIONS --------------------

def load_history():
    if not os.path.exists(HISTORY_FILE):
        save_history([])

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(history, file, indent=4, ensure_ascii=False)


# -------------------- MAIN DASHBOARD --------------------

@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    problem = ""
    history = load_history()

    # Analyze a submitted problem
    if request.method == "POST":
        problem = request.form.get("problem", "").strip()

        if problem:
            failure, confidence = detect_failure(problem)

            if failure is None:
                result = {
                    "failure": "Failure Not Identified",
                    "confidence": "0%",
                    "evidence": [
                        "No matching failure keywords were found."
                    ],
                    "reasoning": (
                        "Please describe the AI/ML problem in more detail."
                    ),
                    "description": (
                        "The system could not identify a known failure type."
                    ),
                    "causes": [],
                    "solutions": []
                }

            else:
                evidence = generate_evidence(problem, failure)
                reasoning = generate_reasoning(failure)
                info = failure_data.get(failure, {})

                failure_name = failure.replace("_", " ").title()

                result = {
                    "failure": failure_name,
                    "confidence": f"{confidence}%",
                    "evidence": evidence,
                    "reasoning": reasoning,
                    "description": info.get(
                        "description",
                        "The model is showing a performance problem."
                    ),
                    "causes": info.get("causes", []),
                    "solutions": info.get("solutions", [])
                }

                # Save only identified failures
                history.insert(0, {
                    "problem": problem,
                    "failure_type": failure_name,
                    "confidence": f"{confidence}%"
                })

                # Keep the latest 100 analyses
                history = history[:100]
                save_history(history)

    # -------------------- ANALYTICS DATA --------------------

    failure_counts = {}

    for item in history:
        name = item.get("failure_type", "Unknown")
        failure_counts[name] = failure_counts.get(name, 0) + 1

    # Data for the failure distribution chart
    chart_data = [
        {"name": name, "count": count}
        for name, count in sorted(
            failure_counts.items(),
            key=lambda item: item[1],
            reverse=True
        )
    ]

    # Summary cards
    total_analyses = len(history)
    unique_failures = len(failure_counts)
    recent_analyses = len(history[:7])
    max_failure_count = max(failure_counts.values(), default=1)

    # Data for recent confidence chart
    recent_history = list(reversed(history[:7]))

    confidence_labels = [
        f"Analysis {i + 1}"
        for i in range(len(recent_history))
    ]

    confidence_values = []

    for item in recent_history:
        confidence = str(item.get("confidence", "0%"))
        confidence = confidence.replace("%", "").strip()

        try:
            confidence_values.append(float(confidence))
        except ValueError:
            confidence_values.append(0)

    return render_template(
        "index.html",
        result=result,
        problem=problem,
        history=history,
        total_analyses=total_analyses,
        unique_failures=unique_failures,
        recent_analyses=recent_analyses,
        max_failure_count=max_failure_count,
        chart_data=chart_data,
        confidence_labels=confidence_labels,
        confidence_values=confidence_values
    )


# -------------------- CLEAR HISTORY --------------------

@app.route("/clear-history", methods=["POST"])
def clear_history():
    save_history([])
    return redirect(url_for("home"))


# -------------------- RUN APPLICATION --------------------

if __name__ == "__main__":
    app.run(debug=True)
