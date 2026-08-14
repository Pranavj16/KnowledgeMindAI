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
    if not v1 or not v2:
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    norm_v1 = math.sqrt(sum(a * a for a in v1))
    norm_v2 = math.sqrt(sum(b * b for b in v2))
    return dot / (norm_v1 * norm_v2) if (norm_v1 and norm_v2) else 0.0


def store_chunks(chunks, document_id=None, user_id=None):
    from .models import DocumentChunk, Document
    collection = get_collection()
    meta = {
        "document_id": str(document_id) if document_id is not None else "",
        "user_id": str(user_id) if user_id is not None else ""
    }
    
    # Clean previous chunks in DB for this document to avoid duplicates on reprocess
    if document_id:
        try:
            DocumentChunk.objects.filter(document_id=document_id).delete()
        except Exception as e:
            print(f"Error clearing previous chunks from DB: {e}")

    for index, chunk in enumerate(chunks):
        embedding = generate_embedding(chunk)
        chunk_id = f"doc_{document_id or 'gen'}_{index}_{uuid.uuid4().hex[:8]}"
        chunk_meta = {**meta, "chunk_index": index}
        
        # 1. Always persist to PostgreSQL Database (Neon)
        if document_id:
            try:
                DocumentChunk.objects.create(
                    document_id=document_id,
                    chunk_index=index,
                    content=chunk,
                    embedding=embedding
                )
            except Exception as e:
                print(f"Error persisting DocumentChunk to PostgreSQL: {e}")

        # 2. Add to ChromaDB vector store
        if collection is not None:
            try:
                collection.add(
                    documents=[chunk],
                    embeddings=[embedding],
                    metadatas=[chunk_meta],
                    ids=[chunk_id]
                )
            except Exception as e:
                print(f"ChromaDB store error: {e}")

        # 3. Add to in-memory cache
        _in_memory_store.append({
            "id": chunk_id,
            "document": chunk,
            "embedding": embedding,
            "document_id": str(document_id) if document_id is not None else None,
            "user_id": str(user_id) if user_id is not None else None,
            "chunk_index": index
        })


def get_total_chunks(document_id=None, user_id=None):
    from .models import DocumentChunk
    try:
        query = DocumentChunk.objects.all()
        if document_id:
            query = query.filter(document_id=document_id)
        elif user_id:
            query = query.filter(document__user_id=user_id)
        count = query.count()
        if count > 0:
            return count
    except Exception:
        pass

    if document_id is not None:
        return sum(1 for item in _in_memory_store if item.get("document_id") == str(document_id))
    return len(_in_memory_store)


def search_chunks(query, document_id=None, user_id=None, n_results=4):
    from .models import DocumentChunk
    query_embedding = generate_embedding(query)
    collection = get_collection()
    
    where_clause = None
    if document_id is not None and str(document_id).strip():
        where_clause = {"document_id": str(document_id)}

    # Attempt ChromaDB query
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
            print(f"ChromaDB query fallback: {e}")

    # Fallback to persistent PostgreSQL DocumentChunk records
    try:
        db_chunks = DocumentChunk.objects.all()
        if document_id:
            db_chunks = db_chunks.filter(document_id=document_id)
        elif user_id:
            db_chunks = db_chunks.filter(document__user_id=user_id)

        scored = []
        for chunk_obj in db_chunks:
            embedding = chunk_obj.embedding
            if not embedding:
                embedding = generate_embedding(chunk_obj.content)
            score = cosine_similarity(query_embedding, embedding)
            scored.append((score, chunk_obj.content))

        if scored:
            scored.sort(key=lambda x: x[0], reverse=True)
            top_docs = [doc for _, doc in scored[:n_results]]
            return {"documents": [top_docs]}
    except Exception as e:
        print(f"PostgreSQL chunk search error: {e}")

    # Final in-memory fallback
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
