import logging

from telegram import Update
from telegram.ext import ApplicationBuilder
from telegram.ext import CommandHandler
from telegram.ext import ContextTypes
from telegram.ext import filters
from telegram.ext import MessageHandler

from config import config
from db import Session
from db.crud import create_customer
from db.crud import get_all_customers
from db.models import Customer
from db.models import TelegramBot
from db.schemas import CustomerCreate
from llm.agents.supervisor import supervisor
from llm.utils import print_stream

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            "Hello! I'm the Instant Beauty assistant! I can help you "
            "with information about our services, scheduling, re-scheduling, canceling "
            "or listing your appointments.\n\n"
            "Let me know what do you need."
        ),
    )


async def get_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    user = update.message.from_user

    # Get the business associated with the bot
    bot_info = await context.bot.get_me()
    with Session() as session:
        bot = (
            session.query(TelegramBot)
            .filter(TelegramBot.telegram_username == bot_info.name)
            .first()
        )
        business_id = bot.business_id

    # Save the user_id
    if "db_user_id" not in context.user_data:
        with Session() as session:
            customers = get_all_customers(
                session,
                [
                    Customer.telegram_name == user["name"],
                    Customer.business_id == business_id,
                ],
            )
            # If the user is not in the DB create a new one
            if not customers:
                customer_create = CustomerCreate(
                    telegram_name=user["name"],
                    business_id=business_id,
                )
                customer_read = create_customer(session, customer_create)
                context.user_data["db_user_id"] = customer_read.id
            else:
                context.user_data["db_user_id"] = customers[0].id

    inputs = {
        "messages": [("user", user_input)],
        "customer_id": context.user_data["db_user_id"],
        "channel": "telegram",
    }
    config = {"configurable": {"thread_id": context.user_data["db_user_id"]}}

    try:
        output = await supervisor.ainvoke(inputs, stream_mode="values", config=config)
        answer = output["messages"][-1].content
        print_stream(output)

    except Exception as e:
        answer = "Sorry there was an error in our system. Try it again later"
        print(f"Error processing the request: {e}")

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=answer,
        # parse_mode=telegram.constants.ParseMode.MARKDOWN_V2,
    )


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Sorry, I didn't understand that command.",
    )


if __name__ == "__main__":
    application = ApplicationBuilder().token(config["telegram"]["api_key"]).build()

    start_handler = CommandHandler("start", start)
    answer_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), get_answer)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)

    application.add_handler(start_handler)
    application.add_handler(answer_handler)
    application.add_handler(unknown_handler)

    application.run_polling()
