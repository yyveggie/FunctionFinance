import json
import requests
from io import BytesIO, StringIO
from datetime import date
import pandas as pd
import numpy as np


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, pd.Timestamp):
            return obj.strftime('%Y-%m-%d %H:%M:%S') if obj is not pd.NaT else None
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, pd.DataFrame):
            return obj.to_dict(orient='records')
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif pd.isna(obj):  # 对 NaN 和 NaT 类型统一处理
            return None
        else:
            return super().default(obj)


def upload_to_file_io(data, file_name):
    if isinstance(data, bytes):
        file_to_upload = BytesIO(data)
    elif isinstance(data, str):
        file_to_upload = StringIO(data)
    elif isinstance(data, dict):
        json_data = json.dumps(data, cls=CustomJSONEncoder)
        file_name = file_name if file_name.endswith(
            '.json') else file_name + '.json'
        file_to_upload = StringIO(json_data)
    else:
        raise ValueError("Data must be of type 'bytes', 'str' or 'dict'")

    response = requests.post(
        'https://file.io',
        files={'file': (file_name, file_to_upload)}
    )

    if response.status_code == 200:
        response_data = response.json()
        if response_data.get('success'):
            return response_data.get('link')
        else:
            return 'File upload failed at file.io'
    else:
        return 'HTTP request failed with status code ' + str(response.status_code)
