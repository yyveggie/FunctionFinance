import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from data_connection.data_upload import upload_to_file_io
from crawler import utils
import uuid
import functools
import json
import pandas as pd

def get_max_split(data_dict):
    max_len = 0
    max_split = None
    
    for split, split_dict in data_dict.items():
        # 首先检查 split_dict 是否是字典且包含 "data" 键
        if isinstance(split_dict, dict) and "data" in split_dict:
            # 然后检查 "data" 键对应的值是否是列表
            if isinstance(split_dict["data"], list):
                data_len = len(split_dict["data"])
                if data_len > max_len:
                    max_len = data_len
                    max_split = split
            else:
                print(f"Warning: '{split}' split's 'data' key is not a list")
        else:
            print(f"Warning: '{split}' split does not have 'data' key or is not a dictionary")
    
    return max_split, max_len


def convert_to_json(data, boundary: int=10):
    current_uuid = str(uuid.uuid4())
    if isinstance(data, pd.DataFrame):
        # 将DataFrame中的NaT替换为None
        data = data.replace({pd.NaT: None})
        data_dict = data.to_dict(orient="split")
        if len(data.index) > boundary:
            link = upload_to_file_io(data=data_dict, file_name=f"request_data_{current_uuid}")
            partial_data = utils.extract_top_x_entries_general(data[:boundary].to_dict(orient="split"), boundary)
            return f"""
I am an AI assistant like you, helping you complete the user's request. This is the data I obtained. Please organize it out and return it to the user.
Here is the data (partial data):
</START>{partial_data}</END>
Here is the download link (full data): {link}
""".strip()
        else:
            return f"""
I am an AI assistant like you, helping you complete the user's request. This is the data I obtained. Please organize it out and return it to the user.
Here is the data:
</START>{data_dict}</END>
""".strip()
    elif isinstance(data, dict):
        max_split, max_len = get_max_split(data)
        if max_len > boundary:
            link = upload_to_file_io(data=data, file_name=f"request_data_{current_uuid}")
            partial_data = utils.extract_top_x_entries_general(dict(list(data.items())[:boundary]), boundary)
            return f"""
I am an AI assistant like you, helping you complete the user's request. This is the data I obtained. Please organize it out and return it to the user.
Here is the data (partial data):
</START>{partial_data}</END>
Here is the download link (full data): {link}
""".strip()
        else:
            return f"""
I am an AI assistant like you, helping you complete the user's request. This is the data I obtained. Please organize it out and return it to the user.
Here is the data:
</START>{json.dumps(data, ensure_ascii=False)}</END>
""".strip()
    elif isinstance(data, (int, float, list)):
        return f"""
I am an AI assistant like you, helping you complete the user's request. This is the data I obtained. Please organize it out and return it to the user.
Here is the data:
</START>{json.dumps(data, ensure_ascii=False)}</END>
""".strip()
    else:
        try:
            return f"""
I am an AI assistant like you, helping you complete the user's request. This is the data I obtained. Please organize it out and return it to the user.
Here is the data:
</START>{json.dumps(data, ensure_ascii=False)}</END>
""".strip()
        except TypeError:
            return f"Unsupported data type: {type(data)}"


# 装饰器，用于处理大量数据
def handle_large_data(boundary: int=10):
    def decorator_handle_large_data(func):
        @functools.wraps(func)
        def wrapper_handle_large_data(*args, **kwargs):
            # 调用原始函数
            result = func(*args, **kwargs)
            # 使用额外参数调用 convert_to_json
            processed_result = convert_to_json(result, boundary=boundary)
            return processed_result
        return wrapper_handle_large_data
    return decorator_handle_large_data
