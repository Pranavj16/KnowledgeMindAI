import os
import hashlib
from google import genai

_genai_client = None


def get_genai_client():
    global _genai_client
    if _genai_client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            try:
                _genai_client = genai.Client(api_key=api_key)
            except Exception as e:
                print(f"GenAI Client error: {e}")
    return _genai_client


def generate_embedding(text):
    client = get_genai_client()
    if client:
        try:
            res = client.models.embed_content(
                model="gemini-embedding-001",
                contents=text
            )
            if hasattr(res, "embeddings") and res.embeddings:
                return list(res.embeddings[0].values)
        except Exception as e:
            print(f"Gemini API embedding error: {e}")

    # Fallback to sentence-transformers if available locally
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2")
        return model.encode(text).tolist()
    except Exception:
        # Lightweight hash vector fallback if no model is available
        h = hashlib.sha256(text.encode('utf-8')).digest()
        return [float(b) / 255.0 for b in h]
