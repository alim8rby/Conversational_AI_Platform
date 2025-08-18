# modules/llm_integration_and_prompting/knowledge_store.py

import os
import json
import pinecone
from pinecone import Pinecone, ServerlessSpec
from pinecone.exceptions import PineconeApiException
from cohere import Client as CohereClient

# --------------------------
# CONFIG & API KEYS (hard‐coded for MVP)
# --------------------------
PINECONE_API_KEY = "PINECONE_API_KEY"
PINECONE_ENV     = "us-east-1"
COHERE_API_KEY   = "COHERE_API_KEY"

# --------------------------
# INITIALIZE COHERE CLIENT
# --------------------------
co = CohereClient(COHERE_API_KEY)

# --------------------------
# INITIALIZE PINECONE CLIENT (v7.x)
# --------------------------
pc = Pinecone(
    api_key=PINECONE_API_KEY,
    environment=PINECONE_ENV
)

# Embedding dimension for Cohere 'embed-multilingual-22' is 768
DIMENSION     = 1024
ICD11_INDEX   = "el-consulto-icd11"
THERAPY_INDEX = "el-consulto-therapy"

# For AWS regions like "us-east-1", use cloud="aws" and region="us-east-1"
cloud  = "aws"
region = PINECONE_ENV
spec   = ServerlessSpec(cloud=cloud, region=region)

# --------------------------
# CREATE INDEXES IF MISSING
# --------------------------
try:
    pc.create_index(
        name=ICD11_INDEX,
        dimension=DIMENSION,
        metric="cosine",
        spec=spec
    )
except PineconeApiException as e:
    # If the index already exists (409), do nothing; else re-raise
    if e.status != 409:
        raise

try:
    pc.create_index(
        name=THERAPY_INDEX,
        dimension=DIMENSION,
        metric="cosine",
        spec=spec
    )
except PineconeApiException as e:
    if e.status != 409:
        raise

# --------------------------
# GET INDEX HANDLES
# --------------------------
icd11_idx   = pc.Index(ICD11_INDEX)
therapy_idx = pc.Index(THERAPY_INDEX)

# --------------------------
# EMBEDDING HELPER
# --------------------------
def embed_text(text: str) -> list[float]:
    """
    Use Cohere’s multilingual-v3.0 to embed any text (English/Arabic/Franco-Arabic).
    Returns a 1024-dimensional list of floats.
    """
    # New model name: "embed-multilingual-v3.0"
    resp = co.embed(
        model="embed-multilingual-v3.0",
        input_type="search_query",   # or "default"; use "search_query" for single-sentence queries
        texts=[text]
    )
    return resp.embeddings[0]

# --------------------------
# UPSERT ICD-11 FROM JSON
# --------------------------
def upsert_icd11_from_json(json_path: str):
    """
    Load ICD-11 JSON (list of {code, name, criteria, lay_description})
    and upsert each entry’s 'criteria' embedding into the ICD11 index.
    """
    with open(json_path, "r", encoding="utf-8") as f:
        icd11_list = json.load(f)

    batch = []
    for entry in icd11_list:
        # Unique ID: “6A70-Depressive-episode”
        entry_id = f"{entry['code']}-{entry['name'].replace(' ', '-')}"
        embedding = embed_text(entry["criteria"])
        metadata = {
            "type": "icd11",
            "code": entry["code"],
            "name": entry["name"],
            "lay_description": entry["lay_description"]
        }
        batch.append((entry_id, embedding, metadata))

        # Upsert in batches of ≤100
        if len(batch) >= 100:
            icd11_idx.upsert(vectors=batch)
            batch = []

    if batch:
        icd11_idx.upsert(vectors=batch)

# --------------------------
# UPSERT THERAPY FROM JSON
# --------------------------
def upsert_therapy_from_json(json_path: str):
    """
    Load therapy modalities JSON (list of {name, description, example_prompt})
    and upsert each entry’s 'description' embedding into the Therapy index.
    """
    with open(json_path, "r", encoding="utf-8") as f:
        therapy_list = json.load(f)

    batch = []
    for entry in therapy_list:
        entry_id = f"THERAPY-{entry['name'].replace(' ', '-')}"
        embedding = embed_text(entry["description"])
        metadata = {
            "type": "therapy",
            "name": entry["name"],
            "example_prompt": entry.get("example_prompt", "")
        }
        batch.append((entry_id, embedding, metadata))

        if len(batch) >= 100:
            therapy_idx.upsert(vectors=batch)
            batch = []

    if batch:
        therapy_idx.upsert(vectors=batch)

# --------------------------
# QUERY FUNCTIONS
# --------------------------
def query_icd11(query: str, top_k: int = 3) -> list[dict]:
    """
    Given a query string, embed it and return the top_k matches
    from the ICD-11 index.
    Returns a list of dicts: [{ 'id', 'score', 'metadata': { … } }, …].
    """
    q_vec = embed_text(query)
    response = icd11_idx.query(
        vector=q_vec,
        top_k=top_k,
        include_metadata=True
    )
    return response.matches

def query_therapy(query: str, top_k: int = 3) -> list[dict]:
    """
    Given a query string, embed it and return the top_k matches
    from the Therapy index.
    Returns a list of dicts: [{ 'id', 'score', 'metadata': { … } }, …].
    """
    q_vec = embed_text(query)
    response = therapy_idx.query(
        vector=q_vec,
        top_k=top_k,
        include_metadata=True
    )
    return response.matches
