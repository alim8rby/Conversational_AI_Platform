import json
import os

from cohere import Client as CohereClient
from pinecone import Pinecone, ServerlessSpec
from pinecone.exceptions import PineconeApiException

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV", "us-east-1")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

ICD11_INDEX = os.getenv("KNOWLEDGE_INDEX", "knowledge-base")
THERAPY_INDEX = os.getenv("DOMAIN_INDEX", "domain-knowledge")
DIMENSION = 1024

if not PINECONE_API_KEY or not COHERE_API_KEY:
    raise RuntimeError("Knowledge-store configuration is missing")

co = CohereClient(COHERE_API_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)
spec = ServerlessSpec(cloud="aws", region=PINECONE_ENV)


def _ensure_index(name: str):
    try:
        pc.create_index(name=name, dimension=DIMENSION, metric="cosine", spec=spec)
    except PineconeApiException as exc:
        if exc.status != 409:
            raise
    return pc.Index(name)


icd11_idx = _ensure_index(ICD11_INDEX)
therapy_idx = _ensure_index(THERAPY_INDEX)


def embed_text(text: str) -> list[float]:
    response = co.embed(
        model="embed-multilingual-v3.0",
        input_type="search_query",
        texts=[text],
    )
    return response.embeddings[0]


def upsert_icd11_from_json(json_path: str):
    with open(json_path, "r", encoding="utf-8") as file:
        entries = json.load(file)

    batch = []
    for entry in entries:
        entry_id = f"{entry['code']}-{entry['name'].replace(' ', '-')}"
        batch.append(
            (
                entry_id,
                embed_text(entry["criteria"]),
                {
                    "type": "knowledge",
                    "code": entry["code"],
                    "name": entry["name"],
                    "description": entry.get("lay_description", ""),
                },
            )
        )
        if len(batch) >= 100:
            icd11_idx.upsert(vectors=batch)
            batch = []

    if batch:
        icd11_idx.upsert(vectors=batch)


def upsert_therapy_from_json(json_path: str):
    with open(json_path, "r", encoding="utf-8") as file:
        entries = json.load(file)

    batch = []
    for entry in entries:
        entry_id = f"KNOWLEDGE-{entry['name'].replace(' ', '-')}"
        batch.append(
            (
                entry_id,
                embed_text(entry["description"]),
                {
                    "type": "domain_knowledge",
                    "name": entry["name"],
                    "example_prompt": entry.get("example_prompt", ""),
                },
            )
        )
        if len(batch) >= 100:
            therapy_idx.upsert(vectors=batch)
            batch = []

    if batch:
        therapy_idx.upsert(vectors=batch)


def query_icd11(query: str, top_k: int = 3) -> list[dict]:
    return icd11_idx.query(
        vector=embed_text(query), top_k=top_k, include_metadata=True
    ).matches


def query_therapy(query: str, top_k: int = 3) -> list[dict]:
    return therapy_idx.query(
        vector=embed_text(query), top_k=top_k, include_metadata=True
    ).matches
