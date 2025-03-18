from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def index() -> dict[str, str]:
    return {"detail": "Hello, world!"}
