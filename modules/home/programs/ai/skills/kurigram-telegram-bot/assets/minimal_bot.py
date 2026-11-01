"""Run with API_ID, API_HASH and BOT_TOKEN in the environment."""

import asyncio
import os
from pyrogram import Client, filters, idle


def register(app):
    @app.on_message(filters.private & filters.command("start"))
    async def start(client, message):
        await message.reply_text("Ready.")

    return start


async def main():
    app = Client(
        "minimal-bot",
        api_id=int(os.environ["API_ID"]),
        api_hash=os.environ["API_HASH"],
        bot_token=os.environ["BOT_TOKEN"],
    )
    register(app)
    async with app:
        await idle()


if __name__ == "__main__":
    asyncio.run(main())
