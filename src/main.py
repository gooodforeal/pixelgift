from fastapi import FastAPI

from src.presentation.routers import auth, boxes, media, public

app = FastAPI(title="Pixelgift API", version="0.1.0")

app.include_router(auth.router)
app.include_router(boxes.router)
app.include_router(media.router)
app.include_router(public.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
