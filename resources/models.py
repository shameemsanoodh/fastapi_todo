from pydantic import BaseModel, Field, validator
from typing import List, Dict
from datetime import datetime
from enum import Enum

class file():
    def __init__(self, name: str, isfile: bool):
        self.name = name
        self.isfile = isfile


class MultiLogs(BaseModel):
    log_fields: List[str]
    log_records: List[tuple]

    class Config:
        schema_extra = {
            "example": {
                "log_fields": ["log_eventtime", "log_level", "log_type", "log_id", "log_message"],
                "log_records": [("2022-07-07 11:32:51.729778", "INFO", "pod", "1001071", "message1"), ("2022-07-07 11:32:51.729778", "INFO", "pod", "1001071", "message2")]
            }
        }
