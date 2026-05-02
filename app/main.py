from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.core.database import engine, Base, get_db
from app.api import auth, rooms, websocket, keys

Base.metadata.create_all(bind=engine)

# Safe migration — adds reply_to_id if it doesn't exist
def run_migrations():
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE messages ADD COLUMN reply_to_id INTEGER DEFAULT NULL"))
            conn.commit()
            print("Migration: added reply_to_id column")
        except Exception:
            pass  # Column already exists, that's fine

run_migrations()

app = FastAPI(title="CipherChat", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://cipherchat-frontend-eta.vercel.app",
    ],
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
