"""Common API response schemas."""

from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class APIResponse(BaseModel):
    """Generic API response wrapper."""
    success: bool = True
    message: str = "Operation successful"
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Standardized error response schema."""
    status: str = "error"
    message: str
    detail: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
