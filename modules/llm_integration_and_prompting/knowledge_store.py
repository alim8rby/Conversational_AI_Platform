# modules/llm_integration_and_prompting/knowledge_store.py

import os
import json
import pinecone
from cohere import Client as CohereClient
from cohere import CohereClient as CoCohereClient  # alias if needed
from typing import List, Dict

# ------------------------
# CONFIG & INITIALIZATION
# ------------------------
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY") or "pcsk_4sZacU_UpKYjb2sLr8p36QVFWRwNe5eg51xC8znXCx8iatJdznPzoUArhKt85y4wGUj6cY"
PINECONE_ENV = os.getenv("PINECONE_ENV") or "us-east-1"  # e.g. "us-west1-gcp"

# Cohere API key for embeddings
COHERE_API_KEY = os.getenv("COHERE_API_KEY") or "iqrvb7stR01Lv1fOhIawlBfUNGWSrIZI3W9WGDEp"

pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
co = CohereClient(COHERE_API_KEY)

# Index names
ICD11_INDEX = "el-consulto-icd11"
THERAPY_INDEX = "el-consulto-therapy"

# If indexes don’t exist, create them (dimension = 768 for cohere-embedding-multilingual-22)
if ICD11_INDEX not in pinecone.list_indexes():
    pinecone.create_index(name=ICD11_INDEX, dimension=768, metric="cosine")
if THERAPY_INDEX not in pinecone.list_indexes():
    pinecone.create_index(name=THERAPY_INDEX, dimension=768, metric="cosine")

icd11_idx = pinecone.Index(ICD11_INDEX)
therapy_idx = pinecone.Index(THERAPY_INDEX)


# ------------------------
# EMBEDDING & UPSERT HELPERS
# ------------------------
def embed_text(text: str) -> List[float]:
    """
    Use a multilingual embedding model so Arabic, English, Franco-Arabic all embed
    into the same space. We use cohere's 'embed-multilingual-22' model.
    """
    resp = co.embed(model="embed-multilingual-22", texts=[text])
    return resp.embeddings[0]


def upsert_icd11_from_json(json_path: str):
    """
    Load ICD-11 JSON, upsert each entry as (id, embedding, metadata).
    Metadata will include 'code', 'name', and a small 'type'.
    """
    with open(json_path, "r", encoding="utf-8") as f:
        icd11_list = json.load(f)

    vectors = []
    for entry in icd11_list:
        # Use the ICD-11 code as the ID (e.g. "6A70-Depressive-episode")
        entry_id = f"{entry['code']}-{entry['name'].replace(' ', '-')}"
        text_to_embed = entry["criteria"]  # or use "lay_description" whichever you prefer
        embedding = embed_text(text_to_embed)
        meta = {
            "type": "icd11",
            "code": entry["code"],
            "name": entry["name"],
            "lay_description": entry["lay_description"]
        }
        vectors.append((entry_id, embedding, meta))

    # Batch upsert (Pinecone can handle up to ~100 per batch safely)
    for i in range(0, len(vectors), 100):
        batch = vectors[i : i + 100]
        icd11_idx.upsert(vectors=batch)


def upsert_therapy_from_json(json_path: str):
    """
    Load therapy modalities JSON, upsert each entry as (id, embedding, metadata).
    Metadata includes 'type' = 'therapy', 'name', maybe 'example_prompt'.
    """
    with open(json_path, "r", encoding="utf-8") as f:
        therapy_list = json.load(f)

    vectors = []
    for entry in therapy_list:
        entry_id = f"THERAPY-{entry['name'].replace(' ', '-')}"
        text_to_embed = entry["description"]
        embedding = embed_text(text_to_embed)
        meta = {
            "type": "therapy",
            "name": entry["name"],
            "example_prompt": entry.get("example_prompt", "")
        }
        vectors.append((entry_id, embedding, meta))

    for i in range(0, len(vectors), 100):
        batch = vectors[i : i + 100]
        therapy_idx.upsert(vectors=batch)


# ------------------------
# QUERY FUNCTIONS
# ------------------------
def query_icd11(query: str, top_k: int = 3) -> List[Dict]:
    """
    Given a query (e.g. “I can’t sleep and feel hopeless”), embed and return
    the top_k ICD-11 entries (list of { 'id', 'score', 'metadata' }).
    """
    q_vec = embed_text(query)
    res = icd11_idx.query(queries=[q_vec], top_k=top_k, include_metadata=True)
    return res["matches"][0]


def query_therapy(query: str, top_k: int = 3) -> List[Dict]:
    """
    Given a query (e.g. “I always feel anxious”), embed and return the
    top_k therapy modalities (list of { 'id', 'score', 'metadata' }).
    """
    q_vec = embed_text(query)
    res = therapy_idx.query(queries=[q_vec], top_k=top_k, include_metadata=True)
    return res["matches"][0]
