from fastapi import Fastapi

app = Fastapi()

@app.get("/")
def hello():
    return {"msg":"Hello World"}