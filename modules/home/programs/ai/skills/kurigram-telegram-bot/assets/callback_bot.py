"""Owner-checked, in-memory callback flow; use durable transactions when needed."""

import asyncio
import os
import secrets
import time
from dataclasses import dataclass, field
from pyrogram import Client, filters, idle, types
from pyrogram.errors import MessageNotModified


@dataclass
class Action:
    owner: int
    expires: float
    done: bool = False
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)


def register(app):
    actions = {}

    @app.on_message(filters.private & filters.command("task"))
    async def task(client, message):
        if message.from_user is None:
            return
        now = time.monotonic()
        for key in list(actions):
            if actions[key].expires < now:
                del actions[key]
        token = secrets.token_urlsafe(12)
        actions[token] = Action(message.from_user.id, now + 300)
        await message.reply_text(
            "Complete this task?",
            reply_markup=types.InlineKeyboardMarkup(
                [
                    [
                        types.InlineKeyboardButton(
                            "Complete", callback_data=f"task:{token}"
                        )
                    ]
                ]
            ),
        )

    @app.on_callback_query(filters.regex(r"^task:([A-Za-z0-9_-]+)$"))
    async def complete(client, query):
        token = query.matches[0].group(1)
        action = actions.get(token)
        if (
            action is None
            or action.expires < time.monotonic()
            or query.from_user is None
            or query.from_user.id != action.owner
        ):
            await query.answer("Unavailable.", show_alert=True)
            return
        await query.answer()
        async with action.lock:
            if action.done:
                return
            # Replace with a transactional, idempotent service operation.
            action.done = True
            try:
                await query.edit_message_text("Completed.")
            except MessageNotModified:
                pass

    return task, complete


async def main():
    app = Client(
        "callback-bot",
        api_id=int(os.environ["API_ID"]),
        api_hash=os.environ["API_HASH"],
        bot_token=os.environ["BOT_TOKEN"],
    )
    register(app)
    async with app:
        await idle()


if __name__ == "__main__":
    asyncio.run(main())
