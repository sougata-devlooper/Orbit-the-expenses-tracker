try:
    from fastapi import FastAPI  # type: ignore[import]
except ImportError as exc:
    raise ImportError("FastAPI is required to run this application. Install it with `pip install fastapi`") from exc
from app.database.database import engine, Base
from app.routes import auth, expenses, summary, insights
from app.scheduler.jobs import start_scheduler
from contextlib import asynccontextmanager

# Create database tables automatically
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    start_scheduler()
    yield
    # Shutdown logic (if any)

# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Daily Expense Tracker API",
    description="A complete backend for tracking daily expenses, setting limits, and generating insights.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(expenses.router)
app.include_router(summary.router)
app.include_router(insights.router)

from fastapi.staticfiles import StaticFiles
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")


