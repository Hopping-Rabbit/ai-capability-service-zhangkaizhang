"""Pydantic models for request/response validation."""

from typing import Any, Literal
from pydantic import BaseModel, Field


# ============== Request Models ==============

class CapabilityRequest(BaseModel):
    """Request model for capability invocation."""
    
    capability: Literal["text_summary", "text_translate"] = Field(
        ...,
        description="Capability to invoke"
    )
    input: dict[str, Any] = Field(
        ...,
        description="Input parameters for the capability"
    )
    request_id: str | None = Field(
        default=None,
        description="Optional request ID for tracing"
    )


# ============== Response Models ==============

class MetaData(BaseModel):
    """Metadata included in all responses."""
    
    request_id: str
    capability: str
    elapsed_ms: int


class SuccessData(BaseModel):
    """Data wrapper for successful responses."""
    
    result: Any


class ErrorDetail(BaseModel):
    """Error details for failed responses."""
    
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class SuccessResponse(BaseModel):
    """Successful response format."""
    
    ok: Literal[True] = True
    data: SuccessData
    meta: MetaData


class ErrorResponse(BaseModel):
    """Failed response format."""
    
    ok: Literal[False] = False
    error: ErrorDetail
    meta: MetaData


# ============== Capability-Specific Input Models ==============

class TextSummaryInput(BaseModel):
    """Input for text_summary capability."""
    
    text: str = Field(..., min_length=1, description="Text to summarize")
    max_length: int = Field(default=100, ge=10, le=1000, description="Maximum summary length")


class TextTranslateInput(BaseModel):
    """Input for text_translate capability."""
    
    text: str = Field(..., min_length=1, description="Text to translate")
    target_language: str = Field(default="en", description="Target language code (e.g., en, zh, ja)")
    source_language: str | None = Field(default=None, description="Source language code (auto-detect if not provided)")
