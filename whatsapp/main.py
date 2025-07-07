from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse

from config import config
from whatsapp.utils import extract_grouped_messages
from whatsapp.utils import get_answer
from whatsapp.utils import send_whatsapp_message


app = FastAPI()

VERIFY_TOKEN = config["whatsapp"]["verify_token"]  # Used in Meta Portal


@app.get("/webhook")
async def verify_webhook(request: Request):
    """
    Used by Meta (GET) for webhook verification.
    """
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = int(params.get("hub.challenge"))

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge
    return JSONResponse(status_code=403, content={"error": "Verification failed"})


@app.post("/webhook")
async def receive_message(request: Request):
    """
    Called by Meta (POST) when a new message is received.
    """
    payload = await request.json()
    print("Received message:", payload)

    messages = extract_grouped_messages(payload)

    for message in messages:
        waba_id = message["waba_id"]
        user_id = message["user_id"]
        input = message["text"]
        answer = await get_answer(waba_id, user_id, input)
        await send_whatsapp_message(user_id, answer)

    return JSONResponse(status_code=200, content={"status": "received"})
