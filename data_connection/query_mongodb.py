from pymongo import MongoClient

# 连接本地 MongoDB
def connect_mongodb():
    client = MongoClient('localhost', 27017)
    return client

# 获取集合中的所有文档
def get_all_documents(db_name, collection_name):
    client = connect_mongodb()
    db = client[db_name]
    collection = db[collection_name]

    print(f"All documents in {db_name}.{collection_name}:")
    documents = collection.find()
    for doc in documents:
        print(doc)

    client.close()

# 获取集合中最新的文档
def get_latest_document(db_name, collection_name):
    client = connect_mongodb()
    db = client[db_name]
    collection = db[collection_name]

    print(f"\nLatest document in {db_name}.{collection_name}:")
    latest_doc = collection.find_one(sort=[('_id', -1)])
    print(latest_doc)

    client.close()

# 测试函数
if __name__ == "__main__":
    db_name = "News"
    collection_name = "AAPL"

    # get_all_documents(db_name, collection_name)
    get_latest_document(db_name, collection_name)