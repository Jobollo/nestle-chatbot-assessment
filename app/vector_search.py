import os
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_HOST = os.getenv("PINECONE_HOST")
PINECONE_NAMESPACE = "default"

def query_pinecone(question, top_k=3):
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
    # Extract the chunk text (replace 'content' if your field is named differently)
    context_chunks = [hit['fields']['content'] for hit in hits if 'content' in hit['fields']]
    return context_chunks