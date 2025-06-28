from pydantic import BaseModel
from typing import List

# For Swagger UI
# These models define the structure of the request and response for the query endpoint.
class QueryRequest(BaseModel):
    query: str
    language: str = "en"

class QueryResponse(BaseModel):
    sql: str
    db_result: List[dict]
    answer: str
    error: str