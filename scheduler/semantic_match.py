import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
import os
import numpy as np
from openai import AsyncOpenAI
from pinecone import Pinecone
from sklearn.metrics.pairwise import cosine_similarity
from config_loader import OPENAI_API_KEY, OPENAI_EMBEDDING

client = AsyncOpenAI(api_key=OPENAI_API_KEY)
key = os.environ.get("Pinecone_KEY")
pc = Pinecone(api_key=key)

async def _get_vector(text):
    response = await client.embeddings.create(
        input=text,
        model=OPENAI_EMBEDDING,
        dimensions=1024
    )
    return response.data[0].embedding

class VectorBaseSemanticMatch:
    def __init__(self, query):
        self.query = query
        self.k = 8
        self.index = pc.Index("ufap")

    async def __call__(self):
        return await self.similarity_calculate(self.query)

    async def similarity_calculate(self, text):
        vector = await _get_vector(text)
        results = self.index.query(vector=vector, top_k=self.k)
        return results

class localBaseSemanticMatch:
    def __init__(self, query, matched_items):
        self.query = query
        self.matched_items = matched_items
        self.k = 8

    async def _get_query_vector(self):
        """异步获取查询文本的向量表示"""
        return np.array(await _get_vector(self.query)).reshape(1, -1)

    async def similarity_calculate(self):
        """异步计算查询文本与匹配项目的向量相似度,并返回最相似的前k个项目的名称"""
        query_vector = await self._get_query_vector()  # 异步获取查询文本的向量表示
        # 构建匹配项目的向量矩阵
        embeddings_matrix = np.array([item['vector_value'] for item in self.matched_items])
        # 计算余弦相似度
        similarity_scores = cosine_similarity(query_vector, embeddings_matrix).flatten()
        # 获取相似度最高的前 k 个向量的索引
        top_k_indices = similarity_scores.argsort()[-self.k:][::-1]
        # 返回相似度最高的向量的名称
        top_k_names = [self.matched_items[i]['interface_name'] for i in top_k_indices]
        return top_k_names

    async def __call__(self):
        return await self.similarity_calculate()

async def run(query, items):
    try:
        parser = localBaseSemanticMatch(query, items)
        results = await parser()
        return results
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return []