import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from .routes.system import router as system_router
from .routes.analytics import router as analytics_router
from .routes.mindfolios import router as mindfolios_router
from .routers.tradestation import router as tradestation_router
from .routers.tradestation_auth import router as tradestation_auth_router
from .routers.flow import router as flow_router

app = FastAPI(title="Flowmind API", version="1.0")

# CORS sigur (din variabilă de mediu ALLOWED_ORIGINS)
allowed = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000")
allow_origins = [o.strip() for o in allowed.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
def root_redirect():
    return RedirectResponse(url="/api/v1/")


@app.get("/health")
def health() -> dict:
    return {"ok": True}


app.include_router(system_router)
app.include_router(analytics_router)
app.include_router(mindfolios_router)
app.include_router(tradestation_router, prefix="/api")
app.include_router(tradestation_auth_router, prefix="/api")
app.include_router(flow_router, prefix="/api")
# options router commented until properly created in app/routers/
# app.include_router(options_router, prefix="/api")
