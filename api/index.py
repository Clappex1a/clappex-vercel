import os
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

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
async def chat(request: Request):
    try:
        data = await request.json()
        user_message = data.get("message", "")

        # Prepare OpenRouter request
        headers = {
            "Authorization": f"Bearer {os.getenv('API_KEY')}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "mistral:7b-instruct",  # You can change this later
            "messages": [
                {"role": "system", "content": "You are Clappex, a friendly AI assistant."},
                {"role": "user", "content": user_message}
            ]
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(os.getenv("MODEL_API_URL"), headers=headers, json=payload)
            reply = response.json()["choices"][0]["message"]["content"]

        return JSONResponse(content={"reply": reply})

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Vercel-compatible handler
def handler(event, context):
    from mangum import Mangum
    asgi_handler = Mangum(app)
    return asgi_handler(event, context)
