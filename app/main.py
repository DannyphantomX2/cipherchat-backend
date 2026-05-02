from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.api import auth, rooms, websocket, keys

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CipherChat", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(rooms.router)
app.include_router(keys.router)
app.include_router(websocket.router)

@app.get("/health")
def health():
    return {"status": "ok"}
