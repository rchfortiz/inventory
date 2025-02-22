from fastapi import FastAPI

from inventory.controllers.inventory import inventory_router

app = FastAPI()
app.include_router(inventory_router)
