import os
from functools import lru_cache

from pinecone import Pinecone, ServerlessSpec
from pinecone.exceptions import PineconeApiException
from sentence_transformers import SentenceTransformer

from modules.config import get_settings


@lru_cache(maxsize=1)
def _get_index():
    settings = get_settings()
    if not settings.pinecone_api_key:
        raise RuntimeError("PINECONE_API_KEY is required to use conversation memory")

    client = Pinecone(api_key=settings.pinecone_api_key)
    try:
        client.create_index(
            name=settings.memory_index,
            dimension=512,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region=settings.pinecone_region),
        )
    except PineconeApiException as exc:
        if exc.status != 409:
            raise
    return client.Index(settings.memory_index)


@lru_cache(maxsize=1)
def _get_model():
    return SentenceTransformer("sentence-transformers/distiluse-base-multilingual-cased-v1")


def _namespace(user_id: str) -> str:
    return f"user:{user_id}"


def embed_text(text: str) -> list[float]:
    vector = _get_model().encode(text, normalize_embeddings=True)
    return vector.tolist()


def upsert_memory(id: str, text: str, user_id: str, metadata: dict | None = None):
    _get_index().upsert(
        vectors=[(id, embed_text(text), metadata or {})],
        namespace=_namespace(user_id),
    )


def query_memory(user_id: str, query: str, top_k: int = 5) -> list[dict]:
    response = _get_index().query(
        vector=embed_text(query),
        top_k=top_k,
        include_metadata=True,
        namespace=_namespace(user_id),
    )
    return response.matches
