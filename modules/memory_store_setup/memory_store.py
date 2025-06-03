# modules/memory-store-setup/memory_store.py

from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
import time

# ————————————————
# 1) YOUR PINECONE CREDENTIALS
# ————————————————
PINECONE_API_KEY = "pcsk_4sZacU_UpKYjb2sLr8p36QVFWRwNe5eg51xC8znXCx8iatJdznPzoUArhKt85y4wGUj6cY"
PINECONE_ENV    = "us-east-1"    # e.g. "us-west1-gcp" or "asia-southeast1-poc"

# ————————————————
# 2) INDEX SETTINGS
# ————————————————
INDEX_NAME = "el-consulto-memory"
VECTOR_DIM = 512   # because we’ll use a 512‐dimensional SentenceTransformer model

# ————————————————
# 3) INITIALIZE THE NEW PINECONE CLIENT
# ————————————————
#
# This replaces the old `pinecone.init(...)` call.  We create an instance of Pinecone:
#
pc = Pinecone(
    api_key=PINECONE_API_KEY,
    environment=PINECONE_ENV
)

# ————————————————
# 4) CREATE THE INDEX IF IT DOESN’T EXIST
# ————————————————
#
# Using the ServerlessSpec: for GCP, cloud="gcp" and region="us-west1" if your ENV is "us-west1-gcp".
# If your ENV is "asia-southeast1-poc", then cloud="gcp", region="asia-southeast1", etc.
#
# We’ll parse out the “region” portion from PINECONE_ENV by splitting on the first dash.
region = PINECONE_ENV.split("-")[0]  # e.g. "us-west1" or "asia-southeast1"
spec   = ServerlessSpec(cloud="gcp", region=region)

# List all existing indexes (we access `.names()` to get a plain Python list of names)
existing_indexes = pc.list_indexes().names()

if INDEX_NAME not in existing_indexes:
    pc.create_index(
        name=INDEX_NAME,
        dimension=VECTOR_DIM,
        metric="cosine",
        spec=spec
    )

# ————————————————
# 5) GET A HANDLE TO THE INDEX
# ————————————————
#
# We can now talk to that index via pc.Index(...).
#
index = pc.Index(INDEX_NAME)

# — After “index = pc.Index(INDEX_NAME)”, add:
desc = pc.describe_index(INDEX_NAME)
print(f"🔥 Index '{INDEX_NAME}' dimension is: {desc.dimension}")


# ————————————————
# 6) LOAD THE SENTENCE‐TRANSFORMER MODEL
# ————————————————
#
# We will use "distiluse-base-multilingual-cased-v1" for English/Arabic embeddings.
#
model = SentenceTransformer("sentence-transformers/distiluse-base-multilingual-cased-v1")


# ————————————————
# 7) HELPER: EMBED A TEXT SNIPPET
# ————————————————
def embed_text(text: str) -> list[float]:
    """
    Given any text (English/Arabic/mixed), return a normalized 512‐dim vector.
    """
    vec = model.encode(text, normalize_embeddings=True)
    return vec.tolist()


# ————————————————
# 8) HELPER: UPSERT (INSERT/UPDATE) A MEMORY VECTOR
# ————————————————
def upsert_memory(id: str, text: str, metadata: dict = None):
    """
    Embed `text` → upsert into Pinecone index with:
      - id: unique string (e.g. "user123:user:1648131234")
      - metadata: e.g. {"role":"user", "text_snippet": text}
    """
    embedding = embed_text(text)
    single_record = [(id, embedding, metadata or {})]
    index.upsert(vectors=single_record)


# modules/memory-store-setup/memory_store.py

# … (rest of the file up through loading `index` and `model`) …

def query_memory(query: str, top_k: int = 5) -> list[dict]:
    """
    Query Pinecone with the embedding of `query`, return up to top_k matches.
    Returns a list of dicts: [{"id":..., "score":..., "metadata":{...}}, ...].
    """

    # 1) Embed the query text into a 512-dim list:
    query_vec = embed_text(query)

    # 2) Use the new v2 `vector=` argument instead of `queries=[...]`:
    response = index.query(
        vector=query_vec,            # <-- single vector
        top_k=top_k,
        include_metadata=True
    )

    # 3) `response.matches` is now a list of matches directly
    return response.matches
