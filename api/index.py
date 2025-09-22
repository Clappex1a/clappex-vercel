from fastapi import FastAPI
from fastapi.responses import JSONResponse
from mangum import Mangum

app = FastAPI()

@app.get("/")
def home():
    return JSONResponse(content={"message": "Clappex is live on Vercel!"})

@app.post("/chat")
def chat():
    return {"reply": "Hello from Clappex!"}

handler = Mangum(app)
