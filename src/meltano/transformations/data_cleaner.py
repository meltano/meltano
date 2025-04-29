from typing import List, Dict, Any
from pydantic import BaseModel

class CleanConfig(BaseModel):
    required_fields: List[str] = []

def clean_data(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    cleaned = []
    for record in records:
        new_record = {}
        for key, value in record.items():
            if value is not None:
                new_key = key.lower()
                new_record[new_key] = value
        cleaned.append(new_record)
    return cleaned

def validate_data(records: List[Dict[str, Any]], config: CleanConfig) -> bool:
    for record in records:
        for field in config.required_fields:
            if field.lower() not in record:
                return False
    return True
