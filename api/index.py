from fastapi import FastAPI
from fastapi.responses import JSONResponse
from mangum import Mangum  # adapter for serverless

app = FastAPI()

@app.get("/")
def home():
    return JSONResponse(content={"message": "Clappex is live on Vercel!"})

# Add your chatbot route here
@app.post("/chat")
def chat():
    # Your chatbot logic here
    return {"reply": "Hello from Clappex!"}

handler = Mangum(app)
