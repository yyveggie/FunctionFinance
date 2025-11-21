import json
import os
from pinecone import Pinecone, ServerlessSpec

key = os.environ.get("Pinecone_KEY")
pc = Pinecone(api_key=key)

# 检查索引是否存在，如果不存在则创建
if "ufap" not in pc.list_indexes().names():
    pc.create_index(
        name="ufap",
        dimension=1024,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="gcp", region="us-central1"  # 根据实际情况选择适合的 cloud 和 region
        ),
    )

with open("./apis/embeddings_dict.json", "r", encoding="utf-8") as file:
    data = json.load(file)

vectors = [{"id": name, "values": vector} for name, vector in data.items()]

index = pc.Index("ufap")
index.upsert(vectors)
