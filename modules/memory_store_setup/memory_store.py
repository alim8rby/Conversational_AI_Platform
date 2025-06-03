# modules/memory-store-setup/memory_store.py

from sentence_transformers import SentenceTransformer
import pinecone
import time

# ————————————————
# 1) YOUR PINECONE CREDENTIALS
# ————————————————
PINECONE_API_KEY = "pcsk_4sZacU_UpKYjb2sLr8p36QVFWRwNe5eg51xC8znXCx8iatJdznPzoUArhKt85y4wGUj6cY"
PINECONE_ENV     = "us-east-1"    # e.g. "us-west1-gcp" or "asia-southeast1-poc"

# ————————————————
# 2) INDEX SETTINGS
# ————————————————
INDEX_NAME = "el-consulto-memory"
VECTOR_DIM = 512   # because we’ll use a 512‐dimensional SentenceTransformer model

# ————————————————
# 3) INITIALIZE PINECONE CLIENT (v7.x style)
# ————————————————
client = pinecone.Client(
    api_key=PINECONE_API_KEY,
    environment=PINECONE_ENV
)

# ————————————————
# 4) CREATE THE INDEX IF IT DOESN’T EXIST
# ————————————————
existing_indexes = client.list_indexes()  # returns List[str]

if INDEX_NAME not in existing_indexes:
    from pinecone import ServerlessSpec  # v7.x still exports this name

    # Determine cloud from PINECONE_ENV: "us-east-1" → AWS
    spec = ServerlessSpec(cloud="aws", region=PINECONE_ENV)

    client.create_index(
        name=INDEX_NAME,
        dimension=VECTOR_DIM,
        metric="cosine",
        spec=spec
    )

# ————————————————
# 5) GET A HANDLE TO THE INDEX
# ————————————————
index = client.Index(INDEX_NAME)

# Print its dimension to confirm everything loaded correctly
desc = client.describe_index(INDEX_NAME)
print(f"🔥 Index '{INDEX_NAME}' dimension is: {desc.dimension}")

# ————————————————
# 6) LOAD THE SENTENCE‐TRANSFORMER MODEL
# ————————————————
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

# ————————————————
# 9) QUERY FOR TOP-k MEMORIES
# ————————————————
def query_memory(query: str, top_k: int = 5) -> list[dict]:
    """
    Query Pinecone with the embedding of `query`, return up to top_k matches.
    Returns a list of dicts: [{"id":..., "score":..., "metadata":{...}}, ...].
    """
    query_vec = embed_text(query)
    response = index.query(
        vector=query_vec,      # v7.x uses `vector=` instead of `queries=[...]`
        top_k=top_k,
        include_metadata=True
    )
    return response.matches
