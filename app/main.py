from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from app.config import BASE_DIR, UPLOADS_DIR
from app.database import init_db
from app.routers import entries, ai, settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database and tables
    init_db()
    yield

app = FastAPI(
    title="Nhật Ký AI Thực Thời (Multimodal Journal)",
    description="Ứng dụng viết nhật ký đa phương thức bằng Chữ, Âm thanh, Hình ảnh và Trí tuệ Nhân tạo",
    version="1.0.0",
    lifespan=lifespan
)

# Static files
static_dir = BASE_DIR / "static"
templates_dir = BASE_DIR / "templates"

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

# Routers
app.include_router(entries.router)
app.include_router(ai.router)
app.include_router(settings.router)

@app.get("/")
async def root():
    index_file = templates_dir / "index.html"
    return FileResponse(str(index_file))

@app.get("/health")
def health():
    return {"status": "ok", "app": "NhatKyWeb"}
