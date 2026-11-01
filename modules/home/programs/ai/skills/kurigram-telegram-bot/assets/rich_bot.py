"""A real rich table and styled refresh control; no automatic emoji decorations."""

import asyncio
import os
from pyrogram import Client, enums, filters, idle, types as t
from pyrogram.errors import MessageNotModified


def build_report(count: int) -> t.InputRichMessage:
    return t.InputRichMessage(
        blocks=[
            t.InputRichBlockSectionHeading(text="Queue", size=2),
            t.InputRichBlockTable(
                cells=[
                    [
                        t.RichBlockTableCell("State", is_header=True),
                        t.RichBlockTableCell("Count", is_header=True, align="right"),
                    ],
                    [
                        t.RichBlockTableCell("Ready"),
                        t.RichBlockTableCell(str(count), align="right"),
                    ],
                ],
                is_bordered=True,
                is_compact=True,
            ),
            t.InputRichBlockDetails(
                summary="About",
                blocks=[t.InputRichBlockParagraph(text="Refresh edits this message.")],
            ),
            t.InputRichBlockButtons(
                buttons=[
                    t.RichMessageButton(
                        text="Refresh",
                        callback_data="queue:refresh",
                        style=enums.ButtonStyle.PRIMARY,
                    )
                ],
                align="right",
            ),
        ]
    )


def optional_emoji_label():
    """Example fixture only; not used by the bot unless deliberately selected."""
    DEFAULT_CUSTOM_EMOJI_ID = "5875465628285931233"
    return [t.RichTextCustomEmoji(DEFAULT_CUSTOM_EMOJI_ID, "👍"), " Refresh"]


def register(app, get_count):
    @app.on_message(filters.private & filters.command("queue"))
    async def queue(client, message):
        await client.send_rich_message(message.chat.id, build_report(await get_count()))

    @app.on_callback_query(filters.regex(r"^queue:refresh$"))
    async def refresh(client, query):
        # Read-only demo scoped to the private conversation; private reports may
        # still need resource ownership checks in a real application.
        if (
            query.message is None
            or query.from_user is None
            or query.message.chat.id != query.from_user.id
        ):
            await query.answer("Unavailable.", show_alert=True)
            return
        await query.answer()
        try:
            await query.edit_message_text(rich_message=build_report(await get_count()))
        except MessageNotModified:
            pass

    return queue, refresh


async def main():
    app = Client(
        "rich-bot",
        api_id=int(os.environ["API_ID"]),
        api_hash=os.environ["API_HASH"],
        bot_token=os.environ["BOT_TOKEN"],
    )

    async def get_count():
        return 3

    register(app, get_count)
    async with app:
        await idle()


if __name__ == "__main__":
    asyncio.run(main())
