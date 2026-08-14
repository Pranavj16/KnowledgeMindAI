import uuid
import os
import math
from .embeddings import generate_embedding

_client = None
_collection = None
_in_memory_store = []


def get_collection():
    global _client, _collection
    if _collection is None:
        try:
            import chromadb
            db_path = "/tmp/chroma_db" if os.getenv("VERCEL") else "./chroma_db"
            _client = chromadb.PersistentClient(path=db_path)
            _collection = _client.get_or_create_collection(name="knowledge_base")
        except Exception as e:
            print(f"ChromaDB persistent client unavailable: {e}")
            _collection = None
    return _collection


def cosine_similarity(v1, v2):
    dot = sum(a * b for a, b in zip(v1, v2))
    norm_v1 = math.sqrt(sum(a * a for a in v1))
    norm_v2 = math.sqrt(sum(b * b for b in v2))
    return dot / (norm_v1 * norm_v2) if (norm_v1 and norm_v2) else 0.0


def store_chunks(chunks):
    collection = get_collection()
    for chunk in chunks:
        embedding = generate_embedding(chunk)
        chunk_id = str(uuid.uuid4())
        stored_in_chroma = False
        if collection is not None:
            try:
                collection.add(
                    documents=[chunk],
                    embeddings=[embedding],
                    ids=[chunk_id]
                )
                stored_in_chroma = True
            except Exception as e:
                print(f"ChromaDB store error: {e}")

        if not stored_in_chroma:
            _in_memory_store.append({
                "id": chunk_id,
                "document": chunk,
                "embedding": embedding
            })


def get_total_chunks():
    collection = get_collection()
    if collection is not None:
        try:
            return collection.count()
        except Exception:
            pass
    return len(_in_memory_store)


def search_chunks(query):
    query_embedding = generate_embedding(query)
    collection = get_collection()
    if collection is not None:
        try:
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=3
            )
            if results and results.get("documents") and results["documents"][0]:
                return results
        except Exception as e:
            print(f"ChromaDB search error: {e}")

    # Fallback to cosine similarity matching
    scored = []
    for item in _in_memory_store:
        score = cosine_similarity(query_embedding, item["embedding"])
        scored.append((score, item["document"]))

    scored.sort(key=lambda x: x[0], reverse=True)
    top_docs = [doc for _, doc in scored[:3]]
    return {"documents": [top_docs]}
