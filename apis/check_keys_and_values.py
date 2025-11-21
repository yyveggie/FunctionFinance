import os
import json
from collections import defaultdict

from pprint import pprint


def check_json_keys(directory):
    unique_keys = set()
    key_variation_files = []

    # Walk through the directory to find all json files
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".json"):
                # Construct file path
                file_path = os.path.join(root, file)
                # Read the json file
                with open(file_path, "r", encoding="utf-8") as json_file:
                    data = json.load(json_file)
                    # Assuming all json files have a list of dictionaries
                    if data and isinstance(data, list):
                        # Check the keys in the first dictionary of the list
                        current_keys = set(data[0].keys())
                        if not unique_keys:
                            # Initialize the unique_keys with the first file's keys
                            unique_keys = current_keys
                        elif current_keys != unique_keys:
                            # If current file's keys differ from the seen keys, add to list
                            key_variation_files.append(file)

    return unique_keys, key_variation_files


def replace_key_name(directory, old_key, new_key):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as json_file:
                    data = json.load(json_file)
                modified = False
                if data and isinstance(data, list):
                    for item in data:
                        if old_key in item:
                            item[new_key] = item.pop(old_key)
                            modified = True
                if modified:
                    with open(file_path, "w", encoding="utf-8") as json_file:
                        json.dump(data, json_file,
                                  ensure_ascii=False, indent=4)


def collect_unique_values(directory, skip_keys=None):
    if skip_keys is None:
        skip_keys = ["interface_name", "description"]  # 默认跳过的键
    unique_values = defaultdict(set)

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as json_file:
                    data = json.load(json_file)
                if data and isinstance(data, list):
                    for item in data:
                        for key, value in item.items():
                            if key in skip_keys:
                                continue
                            if isinstance(value, str) and "," in value:
                                values = [v.strip() for v in value.split(",")]
                                for v in values:
                                    unique_values[key].add(v)
                            elif isinstance(value, list):
                                for elem in value:
                                    unique_values[key].add(elem)
                            else:
                                unique_values[key].add(value)
    unique_values = {key: list(values)
                     for key, values in unique_values.items()}
    return unique_values


def find_files_with_key_value(directory, key, value):
    matching_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as json_file:
                    data = json.load(json_file)

                if data and isinstance(data, list):
                    for item in data:
                        if isinstance(item.get(key, ""), str) and "," in item.get(
                            key, ""
                        ):
                            values = [v.strip() for v in item[key].split(",")]
                            if value in values:
                                parent_folder = os.path.basename(root)
                                matching_files.append((parent_folder, file))
                                break
                        elif item.get(key) == value:
                            parent_folder = os.path.basename(root)
                            matching_files.append((parent_folder, file))
                            break
                        elif isinstance(item.get(key, []), list) and value in item.get(
                            key, []
                        ):
                            parent_folder = os.path.basename(root)
                            matching_files.append((parent_folder, file))
                            break
    return matching_files


def count_json_dictionaries(directory):
    total_dictionaries = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as json_file:
                    data = json.load(json_file)
                    if isinstance(data, list):  # 假设 JSON 文件中存储的是字典列表
                        total_dictionaries += len(data)
    return total_dictionaries


def replace_value_in_category(directory, key, old_value, new_value):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as json_file:
                    data = json.load(json_file)
                modified = False
                if data and isinstance(data, list):
                    for item in data:
                        # 检查是否存在指定键，并且对应的值等于 old_value
                        if item.get(key) == old_value:
                            item[key] = new_value
                            modified = True
                if modified:
                    with open(file_path, "w", encoding="utf-8") as json_file:
                        json.dump(data, json_file,
                                  ensure_ascii=False, indent=4)


def add_keyword_if_in_description(directory, character, keyword):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as json_file:
                    data = json.load(json_file)
                modified = False
                if data and isinstance(data, list):
                    for item in data:
                        # 检查 description 中是否包含指定字符
                        if character in item.get("description", ""):
                            # 如果已存在 additional_keywords 键，则添加到其值中；否则，创建新键
                            if "additional_keywords" in item:
                                # 确保 additional_keywords 是列表格式，然后添加关键字
                                if not isinstance(item["additional_keywords"], list):
                                    item["additional_keywords"] = [
                                        item["additional_keywords"]]
                                item["additional_keywords"].append(keyword)
                            else:
                                item["additional_keywords"] = [keyword]
                            modified = True
                if modified:
                    with open(file_path, "w", encoding="utf-8") as json_file:
                        json.dump(data, json_file,
                                  ensure_ascii=False, indent=4)


def find_duplicate_interface_names(directory):
    interface_names = defaultdict(list)  # 用于存储 interface_name 和对应文件路径的字典
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as json_file:
                    data = json.load(json_file)
                if data and isinstance(data, list):
                    for item in data:
                        if 'interface_name' in item:
                            interface_name = item['interface_name']
                            interface_names[interface_name].append(root)

    duplicate_interfaces = {key: value for key,
                            value in interface_names.items() if len(value) > 1}
    for interface_name, directories in duplicate_interfaces.items():
        print(f'重复的 interface_name "{interface_name}" 出现在以下目录中:')
        for directory in set(directories):  # 使用 set 去除重复的目录名称
            print(f'- {directory}')
    return duplicate_interfaces


def remove_duplicates_from_additional_keywords(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as json_file:
                    data = json.load(json_file)
                modified = False  # 用于跟踪文件内容是否被修改
                if data and isinstance(data, list):
                    for item in data:
                        if 'additional_keywords' in item and isinstance(item['additional_keywords'], list):
                            # 删除列表中的重复元素，保持顺序不变
                            unique_keywords = []
                            [unique_keywords.append(x) for x in item['additional_keywords'] if x not in unique_keywords]
                            if len(unique_keywords) != len(item['additional_keywords']):
                                item['additional_keywords'] = unique_keywords
                                modified = True
                if modified:
                    with open(file_path, "w", encoding="utf-8") as json_file:
                        json.dump(data, json_file, ensure_ascii=False, indent=4)


directory = "./apis"
# unique_keys, key_variation_files = check_json_keys(directory)
# print("Unique Keys:", unique_keys)
# print("Files with different keys:", key_variation_files)

# replace_key_name(directory, 'stock_exchange', 'listed_country_or_region')

# unique_values = collect_unique_values(directory)
# pprint(unique_values)

# key = "stock_exchange"
# value = "-"
# matching_files = find_files_with_key_value(directory, key, value)
# print("Matching files:", matching_files)

# total_dictionaries = count_json_dictionaries(directory)
# print(f"Total dictionaries: {total_dictionaries}")

# replace_value_in_category(directory, 'stock_exchange', 'B-Shares', 'China')

# character = "U.S."
# keyword = "US"
# add_keyword_if_in_description(directory, character, keyword)

# duplicate_interface_names = find_duplicate_interface_names(directory)
# print(duplicate_interface_names)

# remove_duplicates_from_additional_keywords(directory)