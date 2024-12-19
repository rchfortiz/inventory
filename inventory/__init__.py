from flask import Flask

from inventory.database import Database

app = Flask(__name__)
db = Database()


@app.get("/")
def index() -> dict[str, str]:
    return {"message": "Hello, world!"}
