import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from pymongo import MongoClient

DATETIME_PATTERNS = [
    re.compile(r"^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}$"),
    re.compile(r"^\d{4}/\d{2}/\d{2}[ T]\d{2}:\d{2}:\d{2}$"),
]
NUMERIC_STRING_PATTERN = re.compile(r"^[+-]?\d+(\.\d+)?$")
EN_WORD_PATTERN = re.compile(r"[A-Za-z0-9]+")
ZH_CHAR_PATTERN = re.compile(r"[\u4e00-\u9fff]")
URL_PATTERN = re.compile(r"https?://|www\.", re.IGNORECASE)


def to_json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, list):
        return [to_json_safe(item) for item in value]
    if isinstance(value, dict):
        return {str(k): to_json_safe(v) for k, v in value.items()}
    return str(value)


def collect_scalar_values(obj: Any, collected: List[Any]) -> None:
    if isinstance(obj, dict):
        for value in obj.values():
            collect_scalar_values(value, collected)
        return

    if isinstance(obj, list):
        for item in obj:
            collect_scalar_values(item, collected)
        return

    collected.append(to_json_safe(obj))


def extract_values_from_data_arrays(data_field: Any) -> List[Any]:
    extracted_values: List[Any] = []

    def walk(obj: Any) -> None:
        if isinstance(obj, dict):
            for value in obj.values():
                walk(value)
            return

        if isinstance(obj, list):
            for item in obj:
                collect_scalar_values(item, extracted_values)
            return

    walk(data_field)
    return extracted_values


def is_datetime_string(text: str) -> bool:
    stripped = text.strip()
    return any(pattern.match(stripped) for pattern in DATETIME_PATTERNS)


def has_minimum_length(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return False

    # If text contains Chinese, require >= 10 Chinese characters.
    zh_chars = ZH_CHAR_PATTERN.findall(stripped)
    if zh_chars:
        return len(zh_chars) >= 10

    # Otherwise, treat as word-based text and require >= 10 words/tokens.
    words = EN_WORD_PATTERN.findall(stripped)
    return len(words) >= 10


def should_keep_value(value: Any) -> bool:
    if value is None:
        return False

    if isinstance(value, bool):
        return False

    if isinstance(value, (int, float)):
        return False

    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return False
        if URL_PATTERN.search(stripped):
            return False
        if is_datetime_string(stripped):
            return False
        if NUMERIC_STRING_PATTERN.match(stripped):
            return False
        if not has_minimum_length(stripped):
            return False
        return True

    return False


def deduplicate_values(values: List[Any]) -> List[Any]:
    """Remove duplicate values while preserving original order."""
    unique_values: List[Any] = []
    seen = set()

    for value in values:
        key = json.dumps(value, ensure_ascii=False, sort_keys=True)
        if key in seen:
            continue
        seen.add(key)
        unique_values.append(value)

    return unique_values


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return str(value)


def extract_values_from_document(doc: Dict[str, Any]) -> List[Any]:
    values: List[Any] = []

    content = doc.get("content")
    if content is not None and normalize_text(content).strip() != "":
        values.append(content)
        return values

    title = doc.get("title")
    if title is not None and normalize_text(title).strip() != "":
        values.append(title)
        return values

    data_field = doc.get("data")
    if data_field is not None:
        values.extend(extract_values_from_data_arrays(data_field))

    return values


def export_news_values(
    host: str,
    port: int,
    db_name: str,
    output_file: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
) -> None:
    if username and password:
        client = MongoClient(f"mongodb://{username}:{password}@{host}:{port}/")
    else:
        client = MongoClient(host, port)

    try:
        db = client[db_name]
        output: Dict[str, Any] = {}

        collection_names = db.list_collection_names()
        for collection_name in collection_names:
            collection = db[collection_name]
            documents = collection.find({}, {"content": 1, "title": 1, "data": 1})

            collection_values: List[Any] = []
            document_count = 0

            for doc in documents:
                document_count += 1
                raw_values = extract_values_from_document(doc)
                filtered_values = [value for value in raw_values if should_keep_value(value)]
                collection_values.extend(filtered_values)

            collection_values = deduplicate_values(collection_values)

            output[collection_name] = {
                "document_count": document_count,
                "value_count": len(collection_values),
                "values": collection_values,
            }

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(output, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(
            f"Export completed. {len(output)} collections were written to {output_path.resolve()}"
        )
    finally:
        client.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Export cleaned news values from MongoDB News database. "
            "Priority per document: content -> title -> data arrays."
        )
    )
    parser.add_argument("--host", default="localhost", help="MongoDB host")
    parser.add_argument("--port", type=int, default=27017, help="MongoDB port")
    parser.add_argument(
        "--db-name",
        default="News",
        help="MongoDB database name (default: News)",
    )
    parser.add_argument(
        "--output",
        default="news_values.json",
        help="Output JSON file path",
    )
    parser.add_argument("--username", default=None, help="MongoDB username")
    parser.add_argument("--password", default=None, help="MongoDB password")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    export_news_values(
        host=args.host,
        port=args.port,
        db_name=args.db_name,
        output_file=args.output,
        username=args.username,
        password=args.password,
    )
