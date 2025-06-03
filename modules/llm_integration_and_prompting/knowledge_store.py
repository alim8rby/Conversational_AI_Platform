# modules/llm_integration_and_prompting/knowledge_store.py

import os
import json
import pinecone
from cohere import Client as CohereClient

# --------------------------
# CONFIG & API KEYS (hard-coded for MVP)
# --------------------------
PINECONE_API_KEY = "pcsk_4sZacU_UpKYjb2sLr8p36QVFWRwNe5eg51xC8znXCx8iatJdznPzoUArhKt85y4wGUj6cY"
PINECONE_ENV     = "us-east-1"
COHERE_API_KEY   = "iqrvb7stR01Lv1fOhIawlBfUNGWSrIZI3W9WGDEp"

# --------------------------
# INITIALIZE COHERE CLIENT
# --------------------------
co = CohereClient(COHERE_API_KEY)

# --------------------------
# INITIALIZE PINECONE CLIENT (v7.x style)
# --------------------------
client = pinecone.Client(
    api_key=PINECONE_API_KEY,
    environment=PINECONE_ENV
)

# Embedding dimension for Cohere 'embed-multilingual-22' is 768
DIMENSION = 768

# Names for our two knowledge indexes
ICD11_INDEX   = "el-consulto-icd11"
THERAPY_INDEX = "el-consulto-therapy"

# Determine cloud/provider from PINECONE_ENV
cloud  = "aws"
region = PINECONE_ENV  # “us-east-1”

from pinecone import ServerlessSpec
spec = ServerlessSpec(cloud=cloud, region=region)

# --------------------------
# CREATE THE INDEXES IF MISSING
# --------------------------
existing_indexes = client.list_indexes()

if ICD11_INDEX not in existing_indexes:
    client.create_index(
        name=ICD11_INDEX,
        dimension=DIMENSION,
        metric="cosine",
        spec=spec
    )

if THERAPY_INDEX not in existing_indexes:
    client.create_index(
        name=THERAPY_INDEX,
        dimension=DIMENSION,
        metric="cosine",
        spec=spec
    )

# --------------------------
# GET HANDLES TO THE INDEXES
# --------------------------
icd11_idx   = client.Index(ICD11_INDEX)
therapy_idx = client.Index(THERAPY_INDEX)

# --------------------------
# EMBEDDING & UPSERT HELPERS
# --------------------------
def embed_text(text: str) -> list[float]:
    """
    Use Cohere’s multilingual-22 to embed any text (English/Arabic/Franco-Arabic).
    Returns a 768-dimensional list of floats.
    """
    resp = co.embed(model="embed-multilingual-22", texts=[text])
    return resp.embeddings[0]

def upsert_icd11_from_json(json_path: str):
    """
    Load ICD-11 JSON (list of {code, name, criteria, lay_description})
    and upsert each entry’s 'criteria' embedding into the ICD-11 index.
    """
    with open(json_path, "r", encoding="utf-8") as f:
        icd11_list = json.load(f)

    vectors = []
    for entry in icd11_list:
        entry_id = f"{entry['code']}-{entry['name'].replace(' ', '-')}"
        embedding = embed_text(entry["criteria"])
        meta = {
            "type": "icd11",
            "code": entry["code"],
            "name": entry["name"],
            "lay_description": entry["lay_description"]
        }
        vectors.append((entry_id, embedding, meta))

    for i in range(0, len(vectors), 100):
        batch = vectors[i : i + 100]
        icd11_idx.upsert(vectors=batch)

def upsert_therapy_from_json(json_path: str):
    """
    Load therapy modalities JSON (list of {name, description, example_prompt})
    and upsert each entry’s 'description' embedding into the Therapy index.
    """
    with open(json_path, "r", encoding="utf-8") as f:
        therapy_list = json.load(f)

    vectors = []
    for entry in therapy_list:
        entry_id = f"THERAPY-{entry['name'].replace(' ', '-')}"
        embedding = embed_text(entry["description"])
        meta = {
            "type": "therapy",
            "name": entry["name"],
            "example_prompt": entry.get("example_prompt", "")
        }
        vectors.append((entry_id, embedding, meta))

    for i in range(0, len(vectors), 100):
        batch = vectors[i : i + 100]
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
