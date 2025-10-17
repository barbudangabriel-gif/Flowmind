from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from .routes.system import router as system_router
from .routes.analytics import router as analytics_router
from .routes.mindfolios import router as mindfolios_router
from .routers.tradestation import router as tradestation_router
from .routers.tradestation_auth import router as tradestation_auth_router

# Import from backend/routers (not app/routers)
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from routers.flow import router as flow_router
from routers.options import router as options_router

app = FastAPI(title="Flowmind API", version="1.0")

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
def root_redirect():
    return RedirectResponse(url="/api/v1/")


app.include_router(system_router)
app.include_router(analytics_router)
app.include_router(mindfolios_router)
app.include_router(tradestation_router, prefix="/api")
app.include_router(tradestation_auth_router, prefix="/api")
app.include_router(flow_router, prefix="/api")
app.include_router(options_router, prefix="/api")
