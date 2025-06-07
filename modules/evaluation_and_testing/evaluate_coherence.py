# modules/evaluation_and_testing/evaluate_coherence.py

import json
import os
from bert_score import score

def load_logs(rel_path="conversation_logs.json"):
    """
    Load conversation logs from a JSON file.
    Assumes the file is located relative to this script.
    """
    base = os.path.dirname(__file__)
    full_path = os.path.join(base, rel_path)
    with open(full_path, encoding="utf-8") as f:
        logs = json.load(f)
    print(f"✅ Loaded {len(logs)} turns from:\n   {full_path}\n")
    return logs

def evaluate():
    """
    Compute BERTScore precision, recall, and F1 for each assistant reply
    against its reference.
    """
    logs = load_logs()
    # Prepare lists of candidate & reference texts
    cands = [turn["assistant"] for turn in logs]
    refs  = [turn["reference"] for turn in logs]

    if not cands or not refs:
        # Nothing to score
        return [], [], []

    # Compute BERTScore (P, R, F1) for English
    P, R, F1 = score(
        cands,
        refs,
        lang="en",      # adjust if your logs are in another language
        verbose=False
    )
    # Convert to Python floats
    return list(P.numpy()), list(R.numpy()), list(F1.numpy())

if __name__ == "__main__":
    P, R, F1 = evaluate()

    if not P:
        print("⚠️ No turns to evaluate. Check that your JSON file is valid and non-empty.")
    else:
        # Print a header
        print("📊 BERTScore results (Precision, Recall, F1):\n")
        for i, (p, r, f) in enumerate(zip(P, R, F1), start=1):
            print(f"Turn {i:02d}: Precision={p:.3f}, Recall={r:.3f}, F1={f:.3f}")
