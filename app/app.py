"""FastAPI entry point for Legal Document Processor."""
import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from server.routes.documents import router as documents_router
from server.routes.upload import router as upload_router
from server.routes.analytics import router as analytics_router
from server.routes.extraction import router as extraction_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Legal Document Processor starting up...")
    yield
    print("Legal Document Processor shutting down...")


app = FastAPI(title="Legal Document Processor", lifespan=lifespan)

# Register API routers
app.include_router(documents_router)
app.include_router(upload_router)
app.include_router(analytics_router)
app.include_router(extraction_router)


@app.get("/api/health")
async def health():
    return {"status": "healthy", "app": "legal-doc-processor"}


# Serve React frontend
frontend_dist = Path(__file__).parent / "frontend" / "dist"
if frontend_dist.exists():
    # Serve static assets (JS, CSS, images)
    assets_dir = frontend_dist / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    # Serve any other static files at root level (favicon, etc.)
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Don't intercept API routes
        if full_path.startswith("api/"):
            return {"error": "Not found"}, 404
        # Try to serve the file directly first
        file_path = frontend_dist / full_path
        if full_path and file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        # Fall back to index.html for SPA routing
        return FileResponse(str(frontend_dist / "index.html"))


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
