from fastapi import FastAPI

app = FastAPI(docs_url=None)


@app.get("/")
async def index() -> dict[str, str]:
    return {"hello": "world"}
