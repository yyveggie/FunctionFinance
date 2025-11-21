from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from datetime import datetime

class AsyncMongoConnection:
    def __init__(self, db_name, host='localhost', port=27017, user=None, password=None):
        if user and password:
            self.client = AsyncIOMotorClient(f'mongodb://{user}:{password}@{host}:{port}/')
        else:
            self.client = AsyncIOMotorClient(f'mongodb://{host}:{port}/')
        self.db = self.client[db_name]

    async def get_collection(self, collection_name):
        return self.db[collection_name]

    async def save_data(self, collection_name, source, data, document_id=None, ordered=True):
        new_entry = {'fetch_time': datetime.now().strftime("%Y%m%d%H%M%S"), 'source': source}
        collection = await self.get_collection(collection_name)
        if isinstance(data, dict):
            new_dict = {**new_entry, **data}
            if document_id:
                return await collection.update_one({'_id': document_id}, {'$set': new_dict}, upsert=True)
            else:
                return await collection.insert_one(new_dict)
        elif isinstance(data, list):
            if data and isinstance(data[0], dict):
                bulk_data = [dict(new_entry, **{k:v for k, v in d.items() if k != '_id'}) for d in data]
                return await collection.insert_many(bulk_data, ordered=ordered)
            elif data and isinstance(data[0], list):
                records = [{**new_entry, **dict(zip(data[0], record))} for record in data[1]]
                return await collection.insert_many(records, ordered=ordered)

class MongoConnection:
    def __init__(self, db_name, host='localhost', port=27017, user=None, password=None):
        if user and password:
            self.client = MongoClient(f'mongodb://{user}:{password}@{host}:{port}/')
        else:
            self.client = MongoClient(f'mongodb://{host}:{port}/')
        self.db = self.client[db_name]

    def get_collection(self, collection_name):
        return self.db[collection_name]

    def save_data(self, collection_name, source, data, document_id=None, ordered=True):
        new_entry = {'fetch_time': datetime.now().strftime("%Y%m%d%H%M%S"), 'source': source}
        collection = self.get_collection(collection_name)
        if isinstance(data, dict):
            new_dict = {**new_entry, **data}
            if document_id:
                return collection.update_one({'_id': document_id}, {'$set': new_dict}, upsert=True)
            else:
                return collection.insert_one(new_dict)
        elif isinstance(data, list):
            if data and isinstance(data[0], dict):
                bulk_data = [dict(new_entry, **{k:v for k, v in d.items() if k != '_id'}) for d in data]
                return collection.insert_many(bulk_data, ordered=ordered)
            elif data and isinstance(data[0], list):
                records = [{**new_entry, **dict(zip(data[0], record))} for record in data[1]]
                return collection.insert_many(records, ordered=ordered)