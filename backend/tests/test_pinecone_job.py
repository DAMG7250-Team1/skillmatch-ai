from pinecone import Pinecone
import os

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))

dummy_vector = [0.1] * 3072

res = index.query(
    vector=dummy_vector,
    top_k=3,
    include_metadata=True,
    namespace=None  # 👈 Try other values too: "default", "jobs"
)

print(f"Found {len(res.matches)} job vectors")
for m in res.matches:
    print(f"✅ {m.id} — {m.metadata.get('job_title')}")
