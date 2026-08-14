import chromadb
import uuid
from sentence_transformers import (
    SentenceTransformer
)
from .embeddings import (
    generate_embedding
)

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


def generate_embedding(text):

    return model.encode(
        text
    ).tolist()

client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_or_create_collection(
    name="knowledge_base"
)


def store_chunks(chunks):

    for chunk in chunks:
        embedding = generate_embedding(
            chunk)
        collection.add(
            documents=[chunk],
            embeddings=[embedding],
            ids=[
                str(uuid.uuid4())
            ]
        )


def get_total_chunks():

    return collection.count()


def search_chunks(query):

    query_embedding = generate_embedding(
        query
    )

    return collection.query(
        query_embeddings=[
            query_embedding
        ],
        n_results=3
    )

    return results