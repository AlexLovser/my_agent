from pydantic import BaseModel
from repository import Level, Space
from enum import Enum

class Status(Enum):
    SUCCESS = "success"
    ERROR = "error"

class Response(BaseModel):
    message: str
    data: list[Level] | list[Space]
    status: Status
