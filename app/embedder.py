import os
import json
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_HOST = os.getenv("PINECONE_HOST")  # Use your index host
NAMESPACE = "default"  # or "" if not using namespaces

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(host=INDEX_HOST)

with open("../data/raw_pages/processed.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Pinecone expects each record to have "_id" and the record field (for integrated embedding)
records = []
for i, doc in enumerate(data):
    text = doc.get("content", "")
    if not text.strip():
        continue  # skip empty content
    records.append({
        "_id": f"{doc.get('type', 'item')}-{i}",
        "content": text,
        "title": doc.get("title", ""),
        "url": doc.get("url", ""),
        "type": doc.get("type", "")
    })


batch_size = 32
for batch_start in range(0, len(records), batch_size):
    batch = records[batch_start: batch_start+batch_size]
    # Only fields "content" will be used for embedding, others as metadata
    try:
        resp = index.upsert_records(
            NAMESPACE,
            batch
        )
        print(f"Batch {batch_start // batch_size + 1}: {resp}")
    except Exception as e:
        print("Error in upsert:", e)
        print(batch)
        break

print("Finished uploading to Pinecone via SDK.")
