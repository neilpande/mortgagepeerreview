from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers.tab1 import router as tab1_router
from .routers.tab2 import router as tab2_router
from .routers.tab3 import router as tab3_router

app = FastAPI(title="Servicer Peer Analytics Dashboard API")

# Read-only, GET-only, no auth/cookies, no sensitive data (public SEC
# filings) -- so a wildcard origin is a reasonable default. Set
# ALLOWED_ORIGINS (comma-separated) in production to restrict it to the
# deployed frontend's actual origin instead.
_default_origins = "http://localhost:5173,http://localhost:5174"
allowed_origins = os.environ.get("ALLOWED_ORIGINS", _default_origins)
origins = ["*"] if allowed_origins == "*" else [o.strip() for o in allowed_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(tab1_router)
app.include_router(tab2_router)
app.include_router(tab3_router)


@app.get("/")
def health():
    # A root route so platform health checks (Render defaults to probing
    # "/") get a 200 instead of a 404 -- without this, the host concludes
    # the instance is unhealthy and kills/restarts it in a loop.
    return {"status": "ok"}
