from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    user_id: int
    text: str

class FileResponse(BaseModel):
    name: Optional[str]
    path: str

class ChatResponse(BaseModel):
    answer: str
    files: Optional[List[FileResponse]] = None