# modules/evaluation_and_testing/evaluate_empathy.py

import json
from transformers import pipeline

def load_logs(path="conversation_logs.json"):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

# ← Use a public empathy classifier instead
empathy_clf = pipeline(
    "text-classification",
    model="paragon-analytics/bert_empathy",
    return_all_scores=True
)

def evaluate():
    logs = load_logs()
    results = []
    for turn in logs:
        text = turn["assistant"]
        scores = empathy_clf(text)[0]   # list of {label, score}
        best = max(scores, key=lambda x: x["score"])
        results.append({
            "reply": text,
            "empathy_label": best["label"],
            "empathy_score": best["score"]
        })
    return results

if __name__ == "__main__":
    for r in evaluate():
        print(
            f"Reply: {r['reply']}\n"
            f"Empathy: {r['empathy_label']} ({r['empathy_score']:.2f})\n"
        )
