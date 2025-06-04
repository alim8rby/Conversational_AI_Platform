from pinecone import Pinecone, ServerlessSpec   # you tried this, but `Client` was missing
from pinecone.exceptions import PineconeApiException
from sentence_transformers import SentenceTransformer
import time

PINECONE_API_KEY = "pcsk_4sZacU_UpKYjb2sLr8p36QVFWRwNe5eg51xC8znXCx8iatJdznPzoUArhKt85y4wGUj6cY"
PINECONE_ENV     = "us-east-1"
INDEX_NAME       = "el-consulto-memory"
VECTOR_DIM       = 512

# You originally wrote:
# client = pinecone.Client(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
# but v7.0.2 no longer exposes `Client`.

# Instead, do:
pc = Pinecone(
    api_key=PINECONE_API_KEY,
    environment=PINECONE_ENV
)

# Determine cloud/region from PINECONE_ENV:
# For “us-east-1” (AWS), set cloud="aws", region="us-east-1"
spec = ServerlessSpec(
    cloud="aws",
    region=PINECONE_ENV
)

# Create index if not exists
try:
    pc.create_index(
        name=INDEX_NAME,
        dimension=VECTOR_DIM,
        metric="cosine",
        spec=spec
    )
except PineconeApiException as e:
    # If the index already exists, skip; otherwise re‐raise
    if e.status != 409:
        raise

# Get a handle to the index
index = pc.Index(INDEX_NAME)

# Print dimension to confirm setup
desc = pc.describe_index(INDEX_NAME)
print(f"🔥 Index '{INDEX_NAME}' dimension is: {desc.dimension}")

# Load multilingual embedding model
model = SentenceTransformer(
    "sentence-transformers/distiluse-base-multilingual-cased-v1"
)

def embed_text(text: str) -> list[float]:
    vec = model.encode(text, normalize_embeddings=True)
    return vec.tolist()

def upsert_memory(id: str, text: str, metadata: dict = None):
    embedding = embed_text(text)
    index.upsert(vectors=[(id, embedding, metadata or {})])

def query_memory(query: str, top_k: int = 5) -> list[dict]:
    q_vec = embed_text(query)
    response = index.query(
        vector=q_vec,
        top_k=top_k,
        include_metadata=True
    )
    return response.matches
