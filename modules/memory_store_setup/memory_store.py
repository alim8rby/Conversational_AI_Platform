import os

from pinecone import Pinecone, ServerlessSpec
from pinecone.exceptions import PineconeApiException
from sentence_transformers import SentenceTransformer

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV", "us-east-1")
INDEX_NAME = os.getenv("MEMORY_INDEX", "conversation-memory")

if not PINECONE_API_KEY:
    raise RuntimeError("Vector database configuration is missing")

pc = Pinecone(api_key=PINECONE_API_KEY)

try:
    pc.create_index(
        name=INDEX_NAME,
        dimension=512,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region=PINECONE_ENV),
    )
except PineconeApiException as exc:
    if exc.status != 409:
        raise

index = pc.Index(INDEX_NAME)
model = SentenceTransformer("sentence-transformers/distiluse-base-multilingual-cased-v1")


def embed_text(text: str) -> list[float]:
    vector = model.encode(text, normalize_embeddings=True)
    return vector.tolist()


def upsert_memory(id: str, text: str, metadata: dict | None = None):
    index.upsert(vectors=[(id, embed_text(text), metadata or {})])


def query_memory(query: str, top_k: int = 5) -> list[dict]:
    response = index.query(
        vector=embed_text(query),
        top_k=top_k,
        include_metadata=True,
    )
    return response.matches
