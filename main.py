from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Bot is live!"}

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    print("Received alert:", data)

    symbol = data.get("symbol")
    side = data.get("side")
    price = data.get("price")

    return {
        "status": "received",
        "symbol": symbol,
        "side": side,
        "price": price
    }
