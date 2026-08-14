import uuid

_model = None
_client = None
_collection = None


def get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def get_collection():
    global _client, _collection
    if _collection is None:
        import chromadb
        _client = chromadb.PersistentClient(path="./chroma_db")
        _collection = _client.get_or_create_collection(name="knowledge_base")
    return _collection


def generate_embedding(text):
    model = get_model()
    return model.encode(text).tolist()


def store_chunks(chunks):
    collection = get_collection()
    for chunk in chunks:
        embedding = generate_embedding(chunk)
        collection.add(
            documents=[chunk],
            embeddings=[embedding],
            ids=[str(uuid.uuid4())]
        )


def get_total_chunks():
    collection = get_collection()
    return collection.count()


def search_chunks(query):
    collection = get_collection()
    query_embedding = generate_embedding(query)
    return collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )