import uvicorn
import os

WORKERS = int(os.getenv("WORKERS") or 2)
PORT = int(os.getenv("PORT") or 8000)
HOST = os.getenv("HOST") or "127.0.0.1"


if __name__ == "__main__":
    uvicorn.run("app:app", host=HOST, port=PORT, workers=WORKERS)
