import uvicorn

from inventory.settings import settings

if __name__ == "__main__":
    uvicorn.run("inventory:app", host=settings.host, port=settings.port, reload=True)
