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
URL_PATTERN = re.compile(r"^/news/", re.IGNORECASE)


def to_json_safe(value: Any) -> Any:
    """Convert unsupported BSON/Python objects into JSON-safe values."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, list):
        return [to_json_safe(item) for item in value]
    if isinstance(value, dict):
        return {str(k): to_json_safe(v) for k, v in value.items()}
    return str(value)


def collect_scalar_values(obj: Any, collected: List[Any]) -> None:
    """Recursively collect scalar values from nested lists/dicts."""
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
    """Extract all values from every array found inside the `data` field."""
    extracted_values: List[Any] = []

    def walk(obj: Any) -> None:
        if isinstance(obj, dict):
            for value in obj.values():
                walk(value)
            return

        if isinstance(obj, list):
            # Requirement focus: for every array, extract values from all fields.
            for item in obj:
                collect_scalar_values(item, extracted_values)
            return

    walk(data_field)
    return extracted_values


def is_datetime_string(text: str) -> bool:
    stripped = text.strip()
    return any(pattern.match(stripped) for pattern in DATETIME_PATTERNS)


def should_keep_value(value: Any) -> bool:
    # Remove null values.
    if value is None:
        return False

    # Remove pure numeric values (int/float).
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return False

    if isinstance(value, str):
        stripped = value.strip()

        # Remove empty strings.
        if not stripped:
            return False

        # Remove date-time strings.
        if is_datetime_string(stripped):
            return False

        # Remove news URLs like /news/xxxx.
        if URL_PATTERN.match(stripped):
            return False

        # Remove text entries with less than 10 words.
        if len(stripped.split()) < 10:
            return False

        return True

    return True


def deduplicate_values(values: List[Any]) -> List[Any]:
    """Remove duplicate values while preserving original order."""
    unique_values: List[Any] = []
    seen_keys = set()

    for value in values:
        key = json.dumps(value, ensure_ascii=False, sort_keys=True)
        if key in seen_keys:
            continue
        seen_keys.add(key)
        unique_values.append(value)

    return unique_values


def export_headline_data_values(
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
            documents = collection.find({"data": {"$exists": True}}, {"_id": 1, "data": 1})

            collection_rows: List[Dict[str, Any]] = []
            collection_total_values = 0
            doc_count = 0

            for doc in documents:
                doc_count += 1
                data_field = doc.get("data")
                values = [
                    value for value in extract_values_from_data_arrays(data_field)
                    if should_keep_value(value)
                ]
                values = deduplicate_values(values)
                collection_total_values += len(values)

                collection_rows.append(
                    {
                        "values": values,
                    }
                )

            output[collection_name] = {
                "document_count": doc_count,
                "total_extracted_values": collection_total_values,
                "documents": collection_rows,
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
            "Export all values from arrays inside the 'data' field for every document "
            "in every collection of the Headline MongoDB database."
        )
    )
    parser.add_argument("--host", default="localhost", help="MongoDB host")
    parser.add_argument("--port", type=int, default=27017, help="MongoDB port")
    parser.add_argument(
        "--db-name",
        default="Headline",
        help="MongoDB database name (default: Headline)",
    )
    parser.add_argument(
        "--output",
        default="headline_data_values.json",
        help="Output JSON file path",
    )
    parser.add_argument("--username", default=None, help="MongoDB username")
    parser.add_argument("--password", default=None, help="MongoDB password")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    export_headline_data_values(
        host=args.host,
        port=args.port,
        db_name=args.db_name,
        output_file=args.output,
        username=args.username,
        password=args.password,
    )
