from fastapi import FastAPI

app = FastAPI(title="Secure Cloud Storage")


@app.get("/health")
def health():
    return {"status": "ok"}
