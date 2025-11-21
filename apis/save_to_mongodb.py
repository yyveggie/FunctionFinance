import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
import os
import json
from data_connection.mongodb import MongoConnection

# 指定stock_data文件夹的路径
stock_data_path = './apis/stock_data'

# 指定包含接口向量化表示的JSON文件路径
vector_json_path = './apis/embeddings_dict.json'

# 创建MongoDB连接
mongo_conn = MongoConnection(db_name='Stock_Data', host='localhost', port=27017)

# 读取接口向量化表示的JSON文件
with open(vector_json_path, 'r') as file:
    vector_data = json.load(file)

# 遍历stock_data文件夹下的所有子文件夹
for folder_name in os.listdir(stock_data_path):
    print(f"Processing folder: {folder_name}")
    
    # 获取集合
    collection = mongo_conn.get_collection(folder_name)
    print(f"Connected to collection: {collection.name}")
    
    # 获取JSON文件路径
    json_file_path = os.path.join(stock_data_path, folder_name, 'interface.json')
    
    # 检查JSON文件是否存在
    if os.path.exists(json_file_path):
        # 读取JSON文件内容
        with open(json_file_path, 'r') as file:
            json_data = json.load(file)
        
        # 遍历JSON数据中的每个字典
        for item in json_data:
            # 将字典转换为MongoDB文档
            document = {
                'interface_name': item['interface_name'],
                'description': item['description'],
                'data_type': item['data_type'],
                'specific_or_all': item['specific_or_all'],
                'frequency': item['frequency'],
                'additional_keywords': item['additional_keywords'],
                'date_type': item['date_type'],
                'listed_country_or_region': item['listed_country_or_region'],
                'folder_name': folder_name
            }
            
            # 在接口向量化表示的字典中查找对应的向量化值
            if item['interface_name'] in vector_data:
                vector_value = vector_data[item['interface_name']]
                # 将向量化值添加到文档中作为新字段
                document['vector_value'] = vector_value
            
            # 将文档插入到集合中
            result = collection.insert_one(document)
            print(f"Inserted document with ID: {result.inserted_id}")
    else:
        print(f"JSON file not found in folder: {folder_name}")