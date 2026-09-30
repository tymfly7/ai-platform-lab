from fastapi import FastAPI

app = FastAPI(title="hell-api")

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.get("/hello/{name}")
def hello(name: str):
    return {"message": f"Hello {name}"}

