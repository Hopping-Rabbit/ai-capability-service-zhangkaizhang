"""FastAPI application entry point."""

import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.logging_config import logger
from app.models import (
    CapabilityRequest,
    SuccessResponse,
    ErrorResponse,
    SuccessData,
    ErrorDetail,
    MetaData
)
from app.handlers import get_handler
from app.exceptions import CapabilityException


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    yield
    logger.info(f"Shutting down {settings.app_name}")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Unified model capability invocation service",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_request_metadata(request: Request, call_next):
    """Add request timing and logging."""
    start_time = time.time()
    
    # Generate request ID if not provided
    request.state.request_id = str(uuid.uuid4())[:8]
    request.state.start_time = start_time
    
    # Log request
    logger.info(f"Request {request.state.request_id} | {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    # Calculate elapsed time
    elapsed_ms = int((time.time() - start_time) * 1000)
    response.headers["X-Request-ID"] = request.state.request_id
    response.headers["X-Elapsed-Ms"] = str(elapsed_ms)
    
    logger.info(f"Request {request.state.request_id} completed in {elapsed_ms}ms")
    
    return response


@app.exception_handler(CapabilityException)
async def capability_exception_handler(request: Request, exc: CapabilityException):
    """Handle custom capability exceptions."""
    elapsed_ms = int((time.time() - request.state.start_time) * 1000)
    
    logger.warning(f"Capability error: {exc.code} - {exc.message}")
    
    response = ErrorResponse(
        ok=False,
        error=ErrorDetail(
            code=exc.code,
            message=exc.message,
            details=exc.details
        ),
        meta=MetaData(
            request_id=request.state.request_id,
            capability=getattr(request.state, "capability", "unknown"),
            elapsed_ms=elapsed_ms
        )
    )
    
    return JSONResponse(
        status_code=400 if exc.code in ["CAPABILITY_NOT_FOUND", "INVALID_INPUT"] else 500,
        content=response.model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    elapsed_ms = int((time.time() - request.state.start_time) * 1000)
    
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    
    response = ErrorResponse(
        ok=False,
        error=ErrorDetail(
            code="INTERNAL_ERROR",
            message="An unexpected error occurred",
            details={"error": str(exc)} if settings.debug else {}
        ),
        meta=MetaData(
            request_id=request.state.request_id,
            capability=getattr(request.state, "capability", "unknown"),
            elapsed_ms=elapsed_ms
        )
    )
    
    return JSONResponse(
        status_code=500,
        content=response.model_dump()
    )


@app.get("/")
async def root():
    """Root endpoint - service info."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "endpoints": {
            "run_capability": "POST /v1/capabilities/run"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/v1/capabilities/run", response_model=SuccessResponse)
async def run_capability(request: Request, body: CapabilityRequest):
    """
    Run a capability with the given input.
    
    ## Capabilities
    
    - **text_summary**: Summarize text to specified max length
      - Input: `{"text": "...", "max_length": 100}`
    
    - **text_translate**: Translate text to target language
      - Input: `{"text": "...", "target_language": "zh", "source_language": "en"}`
    """
    start_time = request.state.start_time
    request_id = body.request_id or request.state.request_id
    request.state.capability = body.capability
    
    # Get handler for the capability
    handler = get_handler(body.capability)
    
    # Execute capability
    result = handler(body.input)
    
    # Calculate elapsed time
    elapsed_ms = int((time.time() - start_time) * 1000)
    
    logger.info(f"Capability {body.capability} executed successfully in {elapsed_ms}ms")
    
    return SuccessResponse(
        ok=True,
        data=SuccessData(result=result),
        meta=MetaData(
            request_id=request_id,
            capability=body.capability,
            elapsed_ms=elapsed_ms
        )
    )
