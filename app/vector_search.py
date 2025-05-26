import os
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_HOST = os.getenv("PINECONE_HOST")
PINECONE_NAMESPACE = "default"

def query_pinecone(question, top_k=5):
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(host=PINECONE_HOST)

    results = index.search(
        namespace=PINECONE_NAMESPACE,
        query={
            "inputs": {"text": question},
            "top_k": top_k
        },
        fields=["title", "url", "type", "content"]
    )

    hits = results['result']['hits']
    # Build a list of dicts with all relevant fields
    context_chunks = []
    for hit in hits:
        fields = hit.get('fields', {})
        # Only add if content exists
        if 'content' in fields and fields['content'].strip():
            chunk = {
                "title": fields.get("title", ""),
                "url": fields.get("url", ""),
                "content": fields["content"]
            }
            context_chunks.append(chunk)
    return context_chunks