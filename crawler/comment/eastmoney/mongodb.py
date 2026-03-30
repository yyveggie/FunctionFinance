import json
import os
from pymongo import MongoClient
from pymongo.errors import BulkWriteError, ServerSelectionTimeoutError


class MongoAPI(object):

    def __init__(self, db_name: str, collection_name: str, host='localhost', port=27017):
        self.host = host
        self.port = port
        self.db_name = db_name
        self.collection_name = collection_name
        self.use_local = False
        self.local_file = f"{self.db_name}_{self.collection_name}.json"

        try:
            # 增加 serverSelectionTimeoutMS，让其在2秒内检测不到MongoDB就主动抛出异常
            self.client = MongoClient(host=self.host, port=self.port, serverSelectionTimeoutMS=2000)
            self.client.server_info()  # 检查是否能够真正连通
            self.database = self.client[self.db_name]
            self.collection = self.database[self.collection_name]
        except Exception as e:
            print(f"[{self.collection_name}] 未检测到/连接失败 MongoDB，启用本地JSON存储 -> {self.local_file} ({e})")
            self.use_local = True
            self._local_data = []
            self._load_local()

    def _load_local(self):
        if os.path.exists(self.local_file):
            try:
                with open(self.local_file, 'r', encoding='utf-8') as f:
                    self._local_data = json.load(f)
            except Exception:
                self._local_data = []
        else:
            self._local_data = []

    def _save_local(self):
        with open(self.local_file, 'w', encoding='utf-8') as f:
            json.dump(self._local_data, f, ensure_ascii=False, indent=2)

    def insert_one(self, kv_dict):
        if self.use_local:
            self._local_data.append(kv_dict)
            self._save_local()
        else:
            self.collection.insert_one(kv_dict)

    def insert_many(self, li_dict):
        if self.use_local:
            # 根据 _id 进行去重插入
            existing_ids = {str(d.get('_id')) for d in self._local_data if '_id' in d}
            for item in li_dict:
                item_id = str(item.get('_id', id(item)))
                if item_id not in existing_ids:
                    self._local_data.append(item)
                    if '_id' in item:
                        existing_ids.add(item_id)
            self._save_local()
        else:
            try:
                self.collection.insert_many(li_dict, ordered=False) # ordered=False 可以在遇到重复 _id 时忽略报错继续插入
            except BulkWriteError:
                pass

    def find_one(self, query1, query2=None):
        if self.use_local:
            for item in self._local_data:
                match = True
                for k, v in query1.items():
                    if item.get(k) != v:
                        match = False
                        break
                if match:
                    return item
            return None
        else:
            return self.collection.find_one(query1, query2)

    def find(self, query1, query2=None):
        if self.use_local:
            results = []
            for item in self._local_data:
                match = True
                for k, v in query1.items():
                    if isinstance(v, dict):
                        continue # 遇到复杂的字典查询 $gte 等在本地模式暂时放行
                    if item.get(k) != v:
                        match = False
                        break
                if match:
                    results.append(item)
            return results
        else:
            return self.collection.find(query1, query2)

    def find_first(self):
        if self.use_local:
            if not self._local_data:
                return None
            return sorted(self._local_data, key=lambda x: str(x.get('_id', '')))[0]
        else:
            return self.collection.find_one(sort=[('_id', 1)])
    
    def find_last(self):
        if self.use_local:
            if not self._local_data:
                return None
            return sorted(self._local_data, key=lambda x: str(x.get('_id', '')))[-1]
        else:
            return self.collection.find_one(sort=[('_id', -1)])

    def count_documents(self):
        if self.use_local:
            return len(self._local_data)
        else:
            return self.collection.count_documents({})

    def update_one(self, kv_dict):
        if not self.use_local:
            self.collection.update_one(kv_dict, {'$set': kv_dict}, upsert=True)

    def drop(self):
        if self.use_local:
            self._local_data = []
            self._save_local()
        else:
            self.collection.drop()
