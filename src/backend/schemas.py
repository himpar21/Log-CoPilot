from pydantic import BaseModel
from typing import List, Dict, Any, Union

class QueryRequest(BaseModel):
    query: str

class Evidence(BaseModel):
    type: str  # e.g., 'log', 'table'
    content: Union[str, Dict[str, Any]]

class QueryResponse(BaseModel):
    summary: str
    evidence: List[Evidence]