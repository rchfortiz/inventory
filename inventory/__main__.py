import uvicorn

if __name__ == "__main__":
    uvicorn.run("inventory:app", interface="wsgi", reload=True)
