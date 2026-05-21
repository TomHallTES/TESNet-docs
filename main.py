from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import docs, admin
import uvicorn

app = FastAPI(title="Tesnet Docs Widget API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to your BigCommerce domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(docs.router, prefix="/api")
app.include_router(admin.router, prefix="/admin")


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
