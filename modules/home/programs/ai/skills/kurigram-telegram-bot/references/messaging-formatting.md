# Ordinary messages, captions and formatting

Use [Rich Messages](rich-messages.md) for structured blocks/tables. Ordinary `send_message` and its parser are a different system. Query the [inventory](api-inventory.md) for exact optional parameters; older Pyrogram/Bot API examples often use the wrong names.

## Sending and message identity

`await app.send_message(chat_id, text, ...) -> Message | None` sends a new message. Keep `(chat_id, message.id)` for a successful result; handle None when Telegram returns no message. `message.reply_text(...)` sends with reply context; `message.answer(...)` sends without the ordinary reply semantics. Inspect bound methods rather than assuming every Client keyword is forwarded. New reply/answer wrappers were expanded in 2.2.26.

Use `ReplyParameters(message_id=...)` for structured replies/quotes; legacy reply_to_message_id and related arguments remain on some methods. Forum message_thread_id and channel direct_messages_topic_id are distinct. A chat ID alone may be insufficient to route to a topic.

`edit_message_text(chat_id, message_id, text=...)` changes one message; `edit_inline_text(inline_message_id, ...)` returns bool. `Message.edit_text` and `CallbackQuery.edit_message_text` fill identifiers. Rich edits use the same methods with `rich_message=InputRichMessage(...)`, omitting text. Repeated identical edits can raise MessageNotModified. Edits can fail because of ownership, deletion, age/context or rights; do not mask all RPCError as “already updated.”

**Pinned implementation caveat:** Client.edit_message_text resets its local `entities` variable to None before parsing, losing caller-supplied explicit entities. Use its supported HTML parsing for ordinary custom entities, or a carefully verified raw messages.EditMessage call if exact entity preservation is required. Convert each high-level entity with `await entity.write()` and pass the resulting raw list; never pass unawaited coroutine objects. Add a regression test before relying on any future fix. CallbackQuery.edit_message_text has no entities parameter at all. This limitation does not prevent rich_message serialization.

`copy_message` creates a separate message without forwarding attribution; `forward_messages` keeps forwarding semantics and can be restricted by protected content. Neither is a universal rich-content preservation guarantee. `delete_messages` returns a count, while bound `Message.delete` returns bool; revocation and chat restrictions apply. Pin/unpin need appropriate rights. Scheduling/repeating is present in method signatures but bot eligibility is not implied; server/account restrictions still apply. Search translate_text, summarize_message, send_reaction and send_poll for their actual result/parameter models.

## Ordinary parsing modes

Explicit `parse_mode=enums.ParseMode.HTML`, MARKDOWN or DISABLED avoids mixed DEFAULT surprises. DEFAULT runs Markdown with HTML enabled. This is **not Bot API MarkdownV2**, and Rich Markdown is another language. Parser.parse coerces to string and strips outer whitespace, including DISABLED mode; explicit entities passed to send_message take a different path. Preserve significant whitespace deliberately and test exact payloads.

Ordinary HTML supports bold/italic/underline/strike aliases, code, pre with `language` attribute, blockquote (including expandable), spoiler/tg-spoiler, anchors/mentions, emoji/tg-emoji and tg-time. The source has TODOs for span class=tg-spoiler and pre/code class=language syntax: do not import the whole Bot API HTML grammar into this local parser. Escape user text with html.escape, including quote=True for attributes. Rich HTML is sent to the server rather than parsed by this local HTML parser.

Explicit `MessageEntity(type=..., offset=..., length=..., ...)` uses UTF-16 code units. Calculate `len(text.encode("utf-16-le")) // 2`, not Python len, for prefix and entity span. Entities and plain text must stay aligned across edits and chunks. Splitting strings without moving entity ranges corrupts surrogate-pair offsets. Basic message and caption limits differ; read the particular send method/source and server constraints instead of applying an HTTP Bot API upload/text limit universally to MTProto.

## Optional custom emoji in bodies, captions and labels

A Unicode emoji is text; a real custom emoji adds an entity referencing a Telegram document. The fixture below is optional, not a request to decorate output or configure every bot:

```python
from pyrogram import enums, types
DEFAULT_CUSTOM_EMOJI_ID = "5875465628285931233"
text = "Status: 👍"
entity = types.MessageEntity(
    type=enums.MessageEntityType.CUSTOM_EMOJI,
    offset=len("Status: ".encode("utf-16-le")) // 2,
    length=len("👍".encode("utf-16-le")) // 2,
    custom_emoji_id=DEFAULT_CUSTOM_EMOJI_ID,
)
# In an authorized running Client:
# await app.send_message(chat_id, text, entities=[entity])
# await app.send_photo(chat_id, photo, caption=text, caption_entities=[entity])
```

HTML alternative: `f'<tg-emoji emoji-id="{DEFAULT_CUSTOM_EMOJI_ID}">👍</tg-emoji>'` with HTML parse mode; supported local alias `<emoji id="...">...</emoji>`. The high-level ID is a decimal **string**; MessageEntity.write converts it to raw MessageEntityCustomEmoji(document_id=int(...)). `get_custom_emoji_stickers([id])` retrieves sticker metadata (up to 200 IDs per call); a valid numeric ID does not grant permission to send it.

Receive from `message.entities` / `caption_entities`, select CUSTOM_EMOJI, preserve its ID plus the exact text span. Sticker custom_emoji_id is metadata, not a reusable file_id. For edits, preserve the whole entity list or regenerate markup; note the edit_message_text entity-reset caveat above.

Optional ordinary icon: `types.InlineKeyboardButton("View", callback_data="view", icon_custom_emoji_id=DEFAULT_CUSTOM_EMOJI_ID)`; KeyboardButton has the same icon property. The writer converts the string to integer raw icon data. No custom-emoji entities can be inserted into these plain-string labels. RichTextCustomEmoji can appear in rich text and restricted rich button labels instead; see [rich interactions](rich-interactions.md).

The current [Telegram formatting specification](https://core.telegram.org/bots/api#formatting-options) restricts bot custom emoji entities/icons to eligible purchased-username bots, or direct private/group/supergroup sends when the bot owner has Premium. Treat these as protocol eligibility conditions, not locally enforced guarantees; exact entitlement and rendering are not established by these offline examples. Preserve a meaningful alternative Unicode emoji and offer a user-approved plain fallback on unsupported contexts. Never assume this fixture ID works in every account or client.

Source: `pyrogram/parser/{parser,html,markdown,utils}.py`, `pyrogram/utils.py:parse_text_entities`, `pyrogram/types/messages_and_media/{message,message_entity}.py`, `pyrogram/methods/messages/{send_message,edit_message_text}.py`, keyboard writers, at [pinned source](provenance.md).
