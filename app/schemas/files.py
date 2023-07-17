
from pydantic import BaseModel
from fastapi import File
from pydantic import BaseModel
from typing import List


class FileUpload(BaseModel):
    name: str
    file: bytes = File(...)


class FileList(BaseModel):
    file_id: int
    file_name: str
