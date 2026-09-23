from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.controllers import admin, applications, auth, matching, profiles, queries, sessions
from app.database import Base, SessionLocal, engine
from app.seed import seed_if_empty


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_if_empty(db)
    finally:
        db.close()
    yield


app = FastAPI(title="PeerUp API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(queries.router)
app.include_router(matching.router)
app.include_router(sessions.router)
app.include_router(profiles.router)
app.include_router(applications.router)
app.include_router(admin.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "peerup-api"}
