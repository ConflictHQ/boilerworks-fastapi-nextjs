from typing import Any

from pydantic import BaseModel


class ApiResponse(BaseModel):
    ok: bool
    data: Any | None = None
    errors: list[dict[str, Any]] | None = None


class FieldError(BaseModel):
    field: str
    messages: list[str]
