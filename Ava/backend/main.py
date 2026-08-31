from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from backend.api.routes import router as api_router
from backend.database import init_db


app = FastAPI(
    title="AVA",
    description="AI Voice Assistant",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


init_db()


# ============================================================
# API Routers
# ============================================================

app.include_router(api_router)


BASE_DIR = Path(__file__).resolve().parent.parent
AUDIO_TEST_AUDIO = BASE_DIR / "audio" / "test.mp3"


@app.get("/audio/test.mp3")
def serve_test_audio():
    return FileResponse(
        AUDIO_TEST_AUDIO,
        media_type="audio/wav",
        filename="test.mp3",
    )


app.mount(
    "/audio",
    StaticFiles(directory=BASE_DIR / "audio"),
    name="audio",
)


@app.get("/notes/{filename}")
def serve_note(filename: str):
    note_path = BASE_DIR / "notes" / filename

    if not note_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="فایل PDF پیدا نشد.",
        )

    return FileResponse(
        note_path,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "inline",
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
    )
