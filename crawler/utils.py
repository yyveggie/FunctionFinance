import pandas as pd
from typing import List, Optional, Any
from data_connection.mongodb import AsyncMongoConnection, MongoConnection

def check_url_sync(collection_name: str, url_list: list[str], source: str):
    db_connection = MongoConnection('URLs')
    collection = db_connection.get_collection(collection_name)
    existing_urls = collection.find(
        {'source': source, 'url': {'$in': url_list}},
        projection={'_id': 0, 'url': 1}
    )
    existing_url_set = set(doc['url'] for doc in existing_urls)
    filtered_urls = [url for url in url_list if url not in existing_url_set]
    return filtered_urls

def save_urls_sync(collection_name: str, url_list: list[str], source: str):
    db_connection = MongoConnection('URLs')
    data = [{'url': url} for url in url_list]
    result = db_connection.save_data(collection_name=collection_name, data=data, source=source)
    return result

async def check_url(collection_name: str, url_list: list[str], source: str):
    db_connection = AsyncMongoConnection('URLs')
    collection = await db_connection.get_collection(collection_name)
    existing_urls = await collection.find(
        {'source': source, 'url': {'$in': url_list}},
        projection={'_id': 0, 'url': 1}
    ).to_list(length=None)
    existing_url_set = set(doc['url'] for doc in existing_urls)
    filtered_urls = [url for url in url_list if url not in existing_url_set]
    return filtered_urls

async def save_urls(collection_name: str, url_list: list[str], source: str):
    db_connection = AsyncMongoConnection('URLs')
    data = [{'url': url} for url in url_list]
    result = await db_connection.save_data(collection_name=collection_name, data=data, source=source)
    return result

def dict_to_split_dict(d, max_rows=None):
    if isinstance(d, dict):
        for key, value in d.items():
            if isinstance(value, dict):
                d[key] = dict_to_split_dict(value)
            elif isinstance(value, list) and all(isinstance(item, dict) for item in value):
                sliced_value = value[:max_rows] if max_rows is not None else value
                d[key] = pd.DataFrame(sliced_value).to_dict(orient='split')
        return d
    elif isinstance(d, list) and all(isinstance(item, dict) for item in d):
        sliced_d = d[:max_rows] if max_rows is not None else d
        return pd.DataFrame(sliced_d).to_dict(orient='split')
    else:
        return d


def extract_top_x_entries_general(data, x):
    """
    A more general function to extract the top 'x' entries from a data structure
    that may contain nested lists or dictionaries to any depth.
    """
    if isinstance(data, list):
        # For lists, return the first 'x' elements
        return [extract_top_x_entries_general(item, x) for item in data[:x]]
    elif isinstance(data, dict):
        # For dictionaries, apply the function to each value
        return {key: extract_top_x_entries_general(value, x) for key, value in data.items()}
    else:
        # If not a list or dict, return the data as is (base case)
        return data


def remove_unwanted_values(data, unwanted_value='Upgrade\n\t\t'):
    if isinstance(data, dict):
        return {k: remove_unwanted_values(v, unwanted_value) for k, v in data.items()}
    elif isinstance(data, list):
        return [remove_unwanted_values(item, unwanted_value) for item in data if item != unwanted_value]
    else:
        return data


def turn_to_one_dict(lis):
    base_keys = list(lis[0].keys())
    collected_dict = {key: [] for key in base_keys}
    for small_dict in lis:
        for key in base_keys:
            collected_dict[key].append(small_dict.get(key))
    return collected_dict

def df_filter(
        df: Optional[pd.DataFrame], 
        condition_column: Optional[str] = None,
        specific_value: Any = None,
        target_columns: Optional[List[str]] = None
    ) -> pd.DataFrame:
    if condition_column is not None and specific_value is not None:
        try:
            condition = df[condition_column] == specific_value
            filtered_df = df.loc[condition]
        except Exception as e:
            filtered_df = df
    else:
        filtered_df = df

    if target_columns is not None:
        try:
            filtered_df = filtered_df[target_columns]
        except Exception as e:
            filtered_df = filtered_df
    return filtered_df