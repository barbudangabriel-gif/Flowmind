from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from .routes.system import router as system_router
from .routes.analytics import router as analytics_router

app = FastAPI(title="Flowmind API", version="1.0")

@app.get("/", include_in_schema=False)
def root_redirect():
    return RedirectResponse(url="/api/v1/")

app.include_router(system_router)
app.include_router(analytics_router)
