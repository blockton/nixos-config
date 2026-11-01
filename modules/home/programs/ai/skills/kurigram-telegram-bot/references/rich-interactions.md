# Rich buttons, callback edits, drafts and ephemeral messages

Start with [Rich Messages](rich-messages.md) for construction/tables. All symbols below are from stable 2.2.26; exact signatures/source links are in the [index](api-inventory.md). Optional runnable UI: [rich_bot.py](../assets/rich_bot.py).

## Rich buttons versus ordinary keyboards

| Representation | Label | Placement / raw representation |
| --- | --- | --- |
| InlineKeyboardButton | str; optional icon_custom_emoji_id | InlineKeyboardMarkup rows; ordinary reply markup |
| KeyboardButton | str; optional icon_custom_emoji_id | ReplyKeyboardMarkup; client input requests |
| RichMessageButton | constrained RichText | PageButton in InputRichBlockButtons or TextButton in RichTextButton |
| RichTextButton | wraps RichMessageButton | Embedded in a paragraph's rich inline text |

RichMessageButton constructor: `text, style=ButtonStyle.DEFAULT, url=None, callback_data=None, web_app=None, login_url=None, switch_inline_query=None, switch_inline_query_current_chat=None, switch_inline_query_chosen_chat=None, copy_text=None, disabled=None`.

Set exactly one action field. The writer enforces this using `is not None`, including empty inline-query strings. Callback data is str or bytes, encoded to bytes; enforce 1–64 bytes before transport. `copy_text` uses CopyTextButton (up to 256 characters); disabled uses DisabledButton(). It has **no pay, callback_game, user_id, requires_password or icon_custom_emoji_id argument**. Do not copy the full InlineKeyboardButton signature.

Styles are enums.ButtonStyle.DEFAULT, PRIMARY, SUCCESS, DANGER and LINK. LINK is a borderless treatment documented only for rich callback buttons. It is not a request to create a URL button. Color is theme-dependent. The writer does not enforce all server label/style/action constraints.

Label content may be strings, custom emoji and formatted date/time, optionally concatenated as a list. Bold, links and arbitrary formatting wrappers are not legal merely because the generic RichText serializer accepts them. Optional fixture example:

```python
from pyrogram import enums, types as t
DEFAULT_CUSTOM_EMOJI_ID = "5875465628285931233"
button = t.RichMessageButton(
    text=[t.RichTextCustomEmoji(DEFAULT_CUSTOM_EMOJI_ID, "👍"), " Refresh"],
    callback_data="report:refresh", style=enums.ButtonStyle.PRIMARY,
)
row = t.InputRichBlockButtons(buttons=[button], align="right")
inline_control = t.InputRichBlockParagraph(text=[
    "More: ", t.RichTextButton(button=t.RichMessageButton(
        text="Details", callback_data="report:details", style=enums.ButtonStyle.LINK,
    )),
])
```

There is no separate rich icon property: custom emoji is part of the allowed label representation. Ordinary buttons have an icon property and plain-string labels. Do not put HTML in their text. Neither form guarantees this fixture's permissions or rendering. Meaningful Unicode alternative text matters.

InputRichBlockButtons is **one row** of 1–8 RichMessageButton objects, with optional left/center/right alignment. Use multiple blocks for multiple rows. The local writer accepts even empty/oversized lists; application validation and server constraints are still needed. A RichTextButton wraps a TextButton; a Buttons block writes PageButton objects. They are not InlineKeyboardMarkup entries.

URL actions open links. Web Apps are restricted to eligible private bot conversations; login URLs require domain/bot authorization and may resolve the configured bot peer. Switch-inline actions have channel/business/direct-message exclusions; consult each constructor docstring. No high-level pay/game rich button exists here. An ordinary keyboard can be used alongside rich content through reply_markup when the requested UX permits it, but is not a substitute for an absent rich action.

## Callback acknowledgement and same-message editing

Rich callback controls produce ordinary CallbackQuery updates. Use `@app.on_callback_query(filters.regex(...))`, acknowledge with `await query.answer()`, validate server-side owner/resource/version, then rebuild the rich input:

```python
# Within an authorized CallbackQuery handler:
# await query.answer()
# await query.edit_message_text(rich_message=build_report(new_state))
```

The bound method routes ordinary and inline-message IDs and returns Message | bool. `Message.edit_text(rich_message=...)` is another bound path. When calling Client directly, omit text entirely: text takes precedence over rich_message. MessageNotModified is a specific harmless outcome only when duplicate edits are expected. Preserve any desired external inline keyboard explicitly when rebuilding edits; do not depend on unspecified omitted-markup behavior.

Do not confuse refreshing the current message with `reply_rich`/`answer_rich`/`send_rich_message`, which create messages. Received RichMessage is not an InputRichMessage; keep an input model and rebuild it. Rich table changes, button disabled states and labels all require editing the containing message rather than mutating Python objects in place.

## Drafts, streaming and stop events

`send_rich_message_draft(chat_id, draft_id, rich_message, message_thread_id=None, can_stop=None, keep_on_stop=None) -> bool` is bot-only per source documentation. It sends messages.SetTyping with InputSendMessageRichMessageDraftAction, not a durable message. draft_id must be nonzero and identifies progressive replacements. No Message or message ID is returned. Finalize with a separate `send_rich_message` call.

```python
from pyrogram import types as t

async def publish_progress(app, chat_id, updates, stop_event):
    draft_id = app.rnd_id() or 1
    latest = None
    async for text in updates:
        if stop_event.is_set():
            return  # Policy: discard partial output; caller may choose to preserve it.
        latest = t.InputRichMessage(blocks=[t.InputRichBlockParagraph(text=text)])
        await app.send_rich_message_draft(
            chat_id, draft_id, latest, can_stop=True, keep_on_stop=False,
        )
    if latest is not None and not stop_event.is_set():
        await app.send_rich_message(chat_id, latest)
```

Production code must map the actual draft_id into state before consumption so a stop handler can set the correct Event. `@app.on_stopped_message_generation()` receives MessageGenerationStopped(chat, message_thread_id, draft_id). Use `(chat.id, thread, draft_id)` to locate the task. Cancellation should stop the producer as well as sending; manage that task explicitly and clean up the mapping in finally. Debounce updates, serialize sends per draft and avoid a flood of one-token RPCs. Recheck cancellation before final persistence; no stop/finalization race can be made globally atomic by this helper.

Drafts are documented as short-lived previews (about 30 seconds); keep_on_stop does not persist them. InputRichBlockThinking is for draft status. Plain `send_message_draft` also exists. **No public Client.stop_message_generation exists**: stopping local generation is application logic responding to the stop update. The upstream draft docstring contains invalid calls omitting rich_message and passing text to send_rich_message; use the checked signatures above instead.

## Ephemeral messages are a separate feature

`EphemeralMessageParameters(receiver_user_id=..., callback_query_id=None, replace_callback_query_message=None)` can be passed to send_rich_message; it chooses raw ephemeral.SendMessage. It is not a draft and not an ordinary persistent edit. Server/account/chat eligibility applies, and parameters in the ordinary-send branch need not all be meaningful in the ephemeral branch.

`edit_ephemeral_message_text(chat_id, receiver_user_id, ephemeral_message_id, text=None, ..., rich_message=None, ...)` and `delete_ephemeral_message(chat_id, receiver_user_id, ephemeral_message_id)` use receiver identity plus the dedicated ephemeral message ID. Ordinary chat/message IDs alone are insufficient. `Message.delete` has an ephemeral-aware path, but `Message.edit_text` should not be assumed to do so: inspect its forwarding before using a bound shortcut. Delivery to the receiver is not guaranteed, especially while offline. replace_callback_query_message must be False for callbacks originating from ephemeral messages; edit those through the dedicated ephemeral methods. A callback-specific ephemeral replacement requires the real callback query ID; never invent it.

No live test established retention, visibility, client support, charge eligibility or account restrictions. Use protocol documentation plus controlled authorized integration testing for those properties. Stable support for these types does not imply arbitrary browser-style interactivity or universal client availability.

Source: `types/bots_and_keyboards/rich_message_button.py`, `types/input_content/input_rich_block.py`, `types/messages_and_media/rich_text.py`, `methods/messages/{send_rich_message,send_rich_message_draft,edit_message_text}.py`, `methods/bots/*ephemeral*`, and dispatcher stop parser; [pinned provenance](provenance.md).
