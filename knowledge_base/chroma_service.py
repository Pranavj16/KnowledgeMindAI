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
            _collection = _client.get_or_create_collection(
                name="knowledge_base_v3",
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            print(f"ChromaDB persistent client unavailable: {e}")
            _collection = None
    return _collection


def cosine_similarity(v1, v2):
    dot = sum(a * b for a, b in zip(v1, v2))
    norm_v1 = math.sqrt(sum(a * a for a in v1))
    norm_v2 = math.sqrt(sum(b * b for b in v2))
    return dot / (norm_v1 * norm_v2) if (norm_v1 and norm_v2) else 0.0


def store_chunks(chunks, document_id=None, user_id=None):
    collection = get_collection()
    meta = {
        "document_id": str(document_id) if document_id is not None else "",
        "user_id": str(user_id) if user_id is not None else ""
    }
    
    for index, chunk in enumerate(chunks):
        embedding = generate_embedding(chunk)
        chunk_id = f"doc_{document_id or 'gen'}_{index}_{uuid.uuid4().hex[:8]}"
        chunk_meta = {**meta, "chunk_index": index}
        stored_in_chroma = False

        if collection is not None:
            try:
                collection.add(
                    documents=[chunk],
                    embeddings=[embedding],
                    metadatas=[chunk_meta],
                    ids=[chunk_id]
                )
                stored_in_chroma = True
            except Exception as e:
                print(f"ChromaDB store error: {e}")
                try:
                    if _client is not None:
                        _client.delete_collection(name="knowledge_base_v3")
                        global _collection
                        _collection = _client.get_or_create_collection(name="knowledge_base_v3")
                        _collection.add(
                            documents=[chunk],
                            embeddings=[embedding],
                            metadatas=[chunk_meta],
                            ids=[chunk_id]
                        )
                        stored_in_chroma = True
                except Exception as exc:
                    print(f"ChromaDB recreate error: {exc}")

        if not stored_in_chroma:
            _in_memory_store.append({
                "id": chunk_id,
                "document": chunk,
                "embedding": embedding,
                "document_id": str(document_id) if document_id is not None else None,
                "user_id": str(user_id) if user_id is not None else None,
                "chunk_index": index
            })


def get_total_chunks(document_id=None):
    collection = get_collection()
    if collection is not None and document_id is None:
        try:
            return collection.count()
        except Exception:
            pass
    
    if document_id is not None:
        return sum(1 for item in _in_memory_store if item.get("document_id") == str(document_id))
    return len(_in_memory_store)


def search_chunks(query, document_id=None, user_id=None, n_results=4):
    query_embedding = generate_embedding(query)
    collection = get_collection()
    
    where_clause = None
    if document_id is not None and str(document_id).strip():
        where_clause = {"document_id": str(document_id)}

    if collection is not None:
        try:
            query_kwargs = {
                "query_embeddings": [query_embedding],
                "n_results": n_results
            }
            if where_clause:
                query_kwargs["where"] = where_clause

            results = collection.query(**query_kwargs)
            if results and results.get("documents") and results["documents"][0]:
                return results
        except Exception as e:
            print(f"ChromaDB search error: {e}")

    # Fallback to cosine similarity matching
    candidate_store = _in_memory_store
    if document_id is not None and str(document_id).strip():
        doc_str = str(document_id)
        candidate_store = [item for item in _in_memory_store if item.get("document_id") == doc_str]
        
    scored = []
    for item in candidate_store:
        score = cosine_similarity(query_embedding, item["embedding"])
        scored.append((score, item["document"]))

    scored.sort(key=lambda x: x[0], reverse=True)
    top_docs = [doc for _, doc in scored[:n_results]]
    return {"documents": [top_docs]}
