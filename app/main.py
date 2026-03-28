import os
from fastapi import FastAPI
from fastapi import Response
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app.api.v1.router import api_router
from app.core.logging import setup_logging
from app.core.telemetry import setup_telemetry
from app.core.middleware import correlation_id_middleware, auth_middleware
from app.monitoring.metrics import prometheus_payload

# -----------------------------
# App Bootstrap
# -----------------------------

setup_logging()

app = FastAPI(
    title="Agentic Loyalty AI Service",
    version="0.1.0",
    openapi_version="3.1.0",
)

setup_telemetry(app)

# -----------------------------
# CORS Configuration
# IMPORTANT: Update origins for your deployment
# For development, localhost is allowed by default
# For production, add your company domain
# Example: "https://loyalty.company.com", "https://loyalty-staging.company.com"
# Can also use environment variable: os.getenv("FRONTEND_URL")
# -----------------------------

def get_cors_origins():
    """Get CORS origins based on environment"""
    environment = os.getenv("ENVIRONMENT", "local")
    
    # Always allow local development
    origins = [
        "http://localhost:8080",
        "http://localhost:8081",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:8081",
    ]
    
    # Add production/staging domains from environment or config
    frontend_urls = os.getenv("FRONTEND_URLS", "").split(",")
    origins.extend([url.strip() for url in frontend_urls if url.strip()])
    
    return origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Middleware
# -----------------------------

app.middleware("http")(correlation_id_middleware)
app.middleware("http")(auth_middleware)


@app.middleware("http")
async def security_headers_middleware(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    response.headers["Cross-Origin-Resource-Policy"] = "same-site"
    if request.url.scheme == "https":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# -----------------------------
# System Endpoints
# -----------------------------

@app.get("/", tags=["system"])
def root():
    return {
        "status": "ok",
        "service": "AI Loyalty Service",
        "version": "1.0.0",
    }


@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "ok"}


@app.get("/version", tags=["system"])
async def version_info():
    return {
        "service": "agentic-loyalty-ai",
        "service_version": "0.1.0",
        "api_version": "v1",
    }


@app.get("/metrics", tags=["monitoring"])
async def metrics():
    payload, content_type = prometheus_payload()
    return Response(content=payload, media_type=content_type)

# -----------------------------
# API Routes
# -----------------------------

app.include_router(api_router, prefix="/api/v1")
