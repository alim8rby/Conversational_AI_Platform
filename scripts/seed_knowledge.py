"""Seed the optional portfolio knowledge collections."""

import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from modules.memory_store_setup.knowledge_store import (
    upsert_icd11_from_json,
    upsert_therapy_from_json,
)


if __name__ == "__main__":
    icd11_json_path = os.path.join(
        project_root, "modules", "memory_store_setup", "icd11_snippets.json"
    )
    upsert_icd11_from_json(icd11_json_path)

    therapy_json_path = os.path.join(
        project_root, "modules", "memory_store_setup", "therapy_modalities.json"
    )
    upsert_therapy_from_json(therapy_json_path)

    print("Knowledge collections seeded successfully.")
