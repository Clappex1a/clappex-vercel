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

        headers = {
            "Authorization": f"apikey {api_key}",
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

@app.post("/book")
async def book(request: Request):
    try:
        data = await request.json()
        print("📥 Incoming data:", data)

        name = data.get("name")
        email = data.get("email")
        time = data.get("time")

        if not name or not email or not time:
            return JSONResponse(content={"error": "Missing name, email, or time"}, status_code=400)

        raw_key = os.getenv("CAL_API_KEY")
        print("🔑 Raw CAL_API_KEY:", repr(raw_key))

        if not raw_key:
            return JSONResponse(content={"error": "CAL_API_KEY not found"}, status_code=500)

        api_key = raw_key.strip()

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        print("📤 Headers:", headers)

        payload = {
            "eventTypeId": os.getenv("CAL_EVENT_TYPE_ID"),
            "name": name,
            "email": email,
            "start": time
        }
        print("📤 Payload:", payload)

        async with httpx.AsyncClient() as client:
            response = await client.post("https://api.cal.com/v1/bookings", headers=headers, json=payload)
            print("📅 Cal.com status:", response.status_code)
            print("📅 Cal.com body:", response.text)

            try:
                data = response.json()
            except Exception as parse_error:
                print("❌ JSON parse error:", parse_error)
                return JSONResponse(content={"error": "Invalid JSON from Cal.com", "raw": response.text}, status_code=500)

            if response.status_code == 200:
                return JSONResponse(content={"success": True, "booking": data})
            else:
                return JSONResponse(content={"success": False, "error": data}, status_code=response.status_code)

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print("🔥 Booking route crashed:\n", error_trace)
        return JSONResponse(content={"error": str(e), "trace": error_trace}, status_code=500)

def handler(event, context):
    from mangum import Mangum
    asgi_handler = Mangum(app)
    return asgi_handler(event, context)
