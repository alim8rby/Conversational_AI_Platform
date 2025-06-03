# scripts/seed_knowledge.py

"""
One-off script to load ICD-11 and therapy modality JSON data
into the Pinecone indexes using functions defined in knowledge_store.py.
"""

import os
import sys

# Ensure that Python can find the 'modules' package at runtime.
# If you run this from the project root, the next two lines append the path to sys.path:
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

# Import the upsert functions from your knowledge_store module
from modules.llm_integration_and_prompting.knowledge_store import (
    upsert_icd11_from_json,
    upsert_therapy_from_json
)

if __name__ == "__main__":
    # 1. Path to the ICD-11 JSON file
    icd11_json_path = os.path.join(project_root, "modules", "memory_store_setup", "icd11_snippets.json")
    print(f"📥 Upserting ICD-11 data from: {icd11_json_path}")
    upsert_icd11_from_json(icd11_json_path)
    print("✅ ICD-11 data upsert completed.\n")

    # 2. Path to the therapy modalities JSON file
    therapy_json_path = os.path.join(project_root, "modules", "memory_store_setup", "therapy_modalities.json")
    print(f"📥 Upserting Therapy Modalities from: {therapy_json_path}")
    upsert_therapy_from_json(therapy_json_path)
    print("✅ Therapy modalities upsert completed.\n")

    print("🎉 All knowledge data has been upserted to Pinecone.")
