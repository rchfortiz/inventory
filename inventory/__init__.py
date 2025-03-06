from fastapi import FastAPI

from inventory.controllers.admin import admin_router
from inventory.controllers.inventory import inventory_router
from inventory.controllers.login import login_router
from inventory.database import lifespan

app = FastAPI(lifespan=lifespan)
app.include_router(admin_router)
app.include_router(inventory_router)
app.include_router(login_router)
