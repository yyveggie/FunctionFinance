import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
import os
import json
import time
from openai import OpenAI
from config_loader import BASE_URL, ZEN_API_KEY, OPENAI_EMBEDDING

embeddings_dict = {}

def read_json_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data:
                        interface_name = item["interface_name"]
                        print(interface_name)
                        client = OpenAI(api_key=ZEN_API_KEY, base_url=BASE_URL)
                        response = client.embeddings.create(
                            input=item["description"],
                            model=OPENAI_EMBEDDING,
                            dimensions=1024,
                        )
                        time.sleep(2)
                        embeddings_dict[interface_name] = response.data[0].embedding


read_json_files("./apis/stock_data")

with open("./apis/embeddings_dict.json", "w", encoding="utf-8") as f:
    json.dump(embeddings_dict, f, ensure_ascii=False, indent=4)
