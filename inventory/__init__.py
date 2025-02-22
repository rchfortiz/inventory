from fastapi import FastAPI

from inventory.controllers.dashboard import dashboard_router

app = FastAPI()
app.include_router(dashboard_router)
