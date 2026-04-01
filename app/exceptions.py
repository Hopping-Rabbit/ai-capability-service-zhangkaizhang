"""Custom exceptions for the capability service."""


class CapabilityException(Exception):
    """Base exception for capability errors."""
    
    def __init__(self, code: str, message: str, details: dict = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class CapabilityNotFoundException(CapabilityException):
    """Raised when requested capability is not found."""
    
    def __init__(self, capability: str):
        super().__init__(
            code="CAPABILITY_NOT_FOUND",
            message=f"Capability '{capability}' not found",
            details={"available_capabilities": ["text_summary", "text_translate"]}
        )


class InvalidInputException(CapabilityException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(
            code="INVALID_INPUT",
            message=message,
            details=details or {}
        )


class ModelServiceException(CapabilityException):
    """Raised when model service call fails."""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(
            code="MODEL_SERVICE_ERROR",
            message=message,
            details=details or {}
        )
