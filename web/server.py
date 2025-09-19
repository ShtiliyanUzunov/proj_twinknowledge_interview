from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn


app = FastAPI(title="Twinknowledge Interview API", version="1.0.0")

# Allow browser clients during local dev; tighten as needed in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/ping")
def ping():
    """Health-check style endpoint.

    Returns a simple JSON payload to confirm the server is responsive.
    """
    return {"message": "pong"}


if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    )


