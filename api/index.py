from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict

app = FastAPI()

# Optional: Allow CORS for frontend testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return JSONResponse(content={"message": "Clappex is live on Vercel!"})

@app.post("/chat")
def chat(payload: Dict):
    return {"reply": "Hello from Clappex!"}

# Vercel-compatible handler
def handler(event, context):
    from mangum import Mangum
    asgi_handler = Mangum(app)
    return asgi_handler(event, context)
