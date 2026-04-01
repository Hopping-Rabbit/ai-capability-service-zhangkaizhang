"""Capability handlers - dispatch to appropriate service."""

from typing import Any
from app.models import TextSummaryInput, TextTranslateInput
from app.services import TextSummaryService, TextTranslateService
from app.exceptions import InvalidInputException, CapabilityNotFoundException


def handle_text_summary(input_data: dict[str, Any]) -> dict[str, Any]:
    """Handle text_summary capability request."""
    # Validate input
    try:
        validated = TextSummaryInput(**input_data)
    except Exception as e:
        raise InvalidInputException(f"Invalid input for text_summary: {str(e)}")
    
    # Process
    result = TextSummaryService.summarize(
        text=validated.text,
        max_length=validated.max_length
    )
    
    return {"result": result}


def handle_text_translate(input_data: dict[str, Any]) -> dict[str, Any]:
    """Handle text_translate capability request."""
    # Validate input
    try:
        validated = TextTranslateInput(**input_data)
    except Exception as e:
        raise InvalidInputException(f"Invalid input for text_translate: {str(e)}")
    
    # Process
    result = TextTranslateService.translate(
        text=validated.text,
        target_language=validated.target_language,
        source_language=validated.source_language
    )
    
    return {"result": result}


# Capability registry
CAPABILITY_HANDLERS = {
    "text_summary": handle_text_summary,
    "text_translate": handle_text_translate,
}


def get_handler(capability: str):
    """Get handler for specified capability."""
    handler = CAPABILITY_HANDLERS.get(capability)
    if not handler:
        raise CapabilityNotFoundException(capability)
    return handler
