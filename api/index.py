import os
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
def home():
    return JSONResponse(content={"message": "Clappex is live on Vercel!"})

# Chat endpoint with OpenRouter AI
@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        user_message = data.get("message", "")

        headers = {
            "Authorization": f"Bearer {os.getenv('API_KEY')}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "openai/gpt-4o",
            "max_tokens": 1000,
            "messages": [
                {"role": "system", "content": "You are Clappex, a friendly AI assistant."},
                {"role": "user", "content": user_message}
            ]
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(os.getenv("MODEL_API_URL"), headers=headers, json=payload)
            print("🔍 OpenRouter raw response:", response.text)
            data = response.json()

            if "choices" in data:
                reply = data["choices"][0]["message"]["content"]
                return JSONResponse(content={"reply": reply})
            else:
                return JSONResponse(content={"error": "OpenRouter response missing 'choices'", "raw": data}, status_code=500)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Booking endpoint with Cal.com
@app.post("/book")
async def book(request: Request):
    try:
        data = await request.json()
        name = data.get("name")
        email = data.get("email")
        time = data.get("time")  # ISO format like "2025-09-23T10:00:00Z"

        headers = {
            "Authorization": f"Bearer {os.getenv('CAL_API_KEY')}",  # ✅ Correct format for Cal.com
            "Content-Type": "application/json"
        }
        print("🔐 Sending headers:", headers)

        payload = {
            "eventTypeId": os.getenv("CAL_EVENT_TYPE_ID"),
            "name": name,
            "email": email,
            "start": time
        }

        async with httpx.AsyncClient() as client:
            response = await client.post("https://api.cal.com/v1/bookings", headers=headers, json=payload)
            print("📅 Cal.com response:", response.text)
            data = response.json()

            if response.status_code == 200:
                return JSONResponse(content={"success": True, "booking": data})
            else:
                return JSONResponse(content={"success": False, "error": data}, status_code=400)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Vercel-compatible handler
def handler(event, context):
    from mangum import Mangum
    asgi_handler = Mangum(app)
    return asgi_handler(event, context)
