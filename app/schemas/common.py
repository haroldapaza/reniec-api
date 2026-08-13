from typing import Any, Literal
from pydantic import BaseModel, Field


class SearchResponse(BaseModel):
    total: int = Field(description="Cantidad devuelta en esta respuesta")
    limit: int
    results: list[dict[str, Any]]


class CombinedResult(BaseModel):
    source: Literal["reniec", "reniec2"]
    data: dict[str, Any]
