from flask import Flask

app = Flask(__name__)


@app.get("/")
def index() -> dict[str, str]:
    return {"message": "Hello, world!"}
