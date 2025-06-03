# scripts/seed_knowledge.py

import os
import sys

# Make sure Python can find 'modules/...' by adding project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

from modules.llm_integration_and_prompting.knowledge_store import (
    upsert_icd11_from_json,
    upsert_therapy_from_json
)

if __name__ == "__main__":
    icd11_json_path = os.path.join(
        project_root, "modules", "memory_store_setup", "icd11_snippets.json"
    )
    print(f"📥 Upserting ICD-11 data from: {icd11_json_path}")
    upsert_icd11_from_json(icd11_json_path)
    print("✅ ICD-11 data upsert completed.\n")

    therapy_json_path = os.path.join(
        project_root, "modules", "memory_store_setup", "therapy_modalities.json"
    )
    print(f"📥 Upserting Therapy Modalities from: {therapy_json_path}")
    upsert_therapy_from_json(therapy_json_path)
    print("✅ Therapy modalities upsert completed.\n")

    print("🎉 All knowledge data has been upserted to Pinecone.")
