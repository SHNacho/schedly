import asyncio
from collections import defaultdict

import httpx

from config import config
from db import Session
from db.crud import create_customer
from db.crud import get_all_customers
from db.models import Customer
from db.models import WhatsappBot
from db.schemas import CustomerCreate
from llm.agents.supervisor import supervisor
from llm.utils import print_stream

WHATSAPP_TOKEN = config["whatsapp"]["api_key"]
PHONE_NUMBER_ID = config["whatsapp"]["phone_number_id"]
API_URL = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"

HEADERS = {
    "Authorization": f"Bearer {WHATSAPP_TOKEN}",
    "Content-Type": "application/json",
}


async def get_answer(waba_id, user_id, input):
    with Session() as session:
        # Get the bot's business
        bot = session.query(WhatsappBot).filter(WhatsappBot.waba_id == waba_id).first()
        business_id = bot.business_id

        # Get the customer
        customers = get_all_customers(
            session,
            [
                Customer.whatsapp_id == user_id,
                Customer.business_id == business_id,
            ],
        )

        # If the user is not in the DB create a new one
        if not customers:
            customer_create = CustomerCreate(
                whatsapp_id=user_id,
                business_id=business_id,
            )
            customer_read = create_customer(session, customer_create)
        else:
            customer_read = customers[0]

    # Create input
    inputs = {
        "messages": [("user", input)],
        "customer_id": customer_read.id,
        "channel": "whatsapp",
    }
    config = {"configurable": {"thread_id": customer_read.id}}

    # Get answer
    output = await supervisor.ainvoke(inputs, stream_mode="values", config=config)
    answer = output["messages"][-1].content

    print_stream(output)
    return answer


async def send_whatsapp_message(recipient_number: str, message: str):
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_number,
        "type": "text",
        "text": {
            "body": message,
        },
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(API_URL, headers=HEADERS, json=payload)
        if response.status_code == 200:
            print("Message sent successfully!")
        else:
            print("Failed to send message:", response.text)


def extract_grouped_messages(payload: dict):
    """
    Group messages by user_id

    Return: list[dict]

    example:
        [
            {
                user_id: str,
                text: str,
                waba_id: str
            },
            ...
        ]
    """
    grouped = defaultdict(dict)

    for entry in payload.get("entry", []):
        waba_id = entry.get("id")
        for change in entry.get("changes", []):
            value = change.get("value", {})
            for msg in value.get("messages", []):
                from_number = msg.get("from")
                body = msg.get("text", {}).get("body", "")
                if from_number and body:
                    grouped[from_number]["waba_id"] = waba_id
                    if "messages" in grouped[from_number]:
                        grouped[from_number]["messages"].append(body)
                    else:
                        grouped[from_number]["messages"] = [body]

    # Convert to the desired list format
    results = []
    for user_id, body in grouped.items():
        text = "\n".join(body.get("messages", []))
        waba_id = body.get("waba_id")
        results.append(
            {
                "user_id": user_id,
                "text": text,
                "waba_id": waba_id,
            },
        )

    return results
