# Handlers, filters and interaction state

Use `from pyrogram import filters, handlers` and `Client.on_*` decorators or `app.add_handler(handlers.MessageHandler(callback, filter), group=0)`. [API index](api-inventory.md) contains every handler and decorator signature.

## Dispatch model and ordering

Dispatcher parses raw updates, associates a high-level handler class, and walks groups in ascending numeric order. Within one group, the first matching handler runs; a normal return stops that group's search, then the next group is considered. This is not a general middleware next() pipeline.

`update.continue_propagation()` raises ContinuePropagation so later handlers in that group may run. `update.stop_propagation()` raises StopPropagation and stops remaining groups. Filters use `&`, `|`, `~`, not Python `and`, `or`, `not`; parenthesize combinations. Boolean composition short-circuits, so a regex match is not guaranteed to exist if an earlier alternative matched.

`filters.command(["start", "help"])` populates `message.command`; `filters.regex(pattern)` populates `update.matches` on supported updates. Command regex metacharacters are escaped in this release. `filters.user`, `filters.chat` and `filters.topic` are mutable set-like filters. Sender users and sender chats differ; channel posts may have no from_user. `filters.private` on callback queries inspects associated message/chat; do not assume it handles an inline-only query with no message.

Custom filters take `(filter, client, update)`:

```python
async def has_owner(flt, client, message):
    return bool(message.from_user and message.from_user.id in flt.owners)
owner_filter = filters.create(has_owner, owners={12345})
```

A callback coroutine is awaited. Synchronous handlers run in the Client executor. A worker processes one queued update while holding its lock; multiple workers permit concurrency. Handler exceptions go to ErrorHandler, not automatically back to Telegram.

## Handler selection

| Update | Handler/decorator family | Important distinction |
| --- | --- | --- |
| New/edited/deleted messages | MessageHandler, EditedMessageHandler, DeletedMessagesHandler | Deleted updates are not complete original messages |
| Callback / inline / chosen result | CallbackQueryHandler, InlineQueryHandler, ChosenInlineResultHandler | Inline callbacks may have only inline_message_id |
| Membership / join requests | ChatMemberUpdatedHandler, ChatJoinRequestHandler | Rights and update delivery depend on bot role |
| Polls / reactions / counts | PollHandler, MessageReactionHandler, MessageReactionCountHandler | Aggregate count updates differ from per-user reactions |
| Checkout / shipping | PreCheckoutQueryHandler, ShippingQueryHandler | Acknowledging is not payment confirmation |
| Business connection/messages | BusinessConnectionHandler, BusinessMessageHandler, EditedBusinessMessageHandler, DeletedBusinessMessagesHandler | Separate from ordinary message handler dispatch |
| Stories / boosts / paid purchases | StoryHandler, ChatBoostHandler, PurchasedPaidMediaHandler | Availability and account eligibility differ |
| Draft stop | StoppedMessageGenerationHandler | Receives MessageGenerationStopped, not a callback query |
| Managed bots / guest messages | ManagedBotUpdatedHandler, GuestMessageHandler | Inspect associated domain permissions |
| Raw updates | RawUpdateHandler | callback(client, update, users, chats) |
| Lifecycle | StartHandler, StopHandler, ConnectHandler, DisconnectHandler | Special lifecycle registration semantics; inspect decorators |
| Exceptions | ErrorHandler / on_error | See actual argument order below |

The dispatcher calls an error callback as `(client, exception, handler, raw_update, users, chats)` in this release. Some ErrorHandler docstring/typing prose disagrees; implementation takes precedence. Pass exception **classes**, e.g. `exceptions=ValueError`, despite permissive annotations. It checks isinstance against handler.exceptions. Error filters are not evaluated in handle_update_handler_exception, so do not rely on one for exception access control.

## Safe callback workflow

Acknowledge promptly with `await query.answer()` or `answer_callback_query(query.id, ...)`; the query ID is not a message ID. Callback data is attacker-controlled input and may be stale, so parse a versioned bounded token, validate resource ownership and expiry from server state, then execute the action once. Callback payloads are limited to 1–64 **UTF-8 bytes**, not characters. Never encode secrets in the payload.

The optional [callback bot](../assets/callback_bot.py) demonstrates authorization from a server-created record, an acknowledgement before service work, duplicate handling and a same-message edit. Production persistence needs a database/version transaction; its in-memory dictionary is only an example. Inline messages need a resource key independent of chat/message IDs.

`await query.edit_message_text("...")` routes between Client.edit_message_text and Client.edit_inline_text. Return type is Message for ordinary callbacks or bool for inline results. Guard missing/inaccessible message contexts before accessing query.message. Rich callbacks use the same callback pathway; see [rich interactions](rich-interactions.md).

## Keyboards, deep links and inline mode

InlineKeyboardMarkup is rows of InlineKeyboardButton objects. ReplyKeyboardMarkup requests/sends ordinary client input; it does not issue callback queries. ForceReply asks the user to reply; it is not an authorization boundary. KeyboardButton contact/location requests are private-chat features. WebAppInfo on inline/reply buttons has chat/account constraints; validate Web App init data server-side using the current Telegram Web Apps specification before trusting identities.

Ordinary inline/reply buttons accept `icon_custom_emoji_id` and `style` in this release. Their labels are plain strings: embedding an emoji ID or HTML tag in text does not create a custom emoji entity. For optional entity/icon examples see [formatting](messaging-formatting.md); rich labels differ in [rich interactions](rich-interactions.md).

Deep links deliver a `/start payload` command. Treat the payload as a short opaque lookup token, validate expiry and intended user, and avoid putting secrets in URLs. `set_bot_commands` configures command menus using BotCommand objects and optional scope/language. Menu button types and web apps are separate APIs in the index.

InlineQueryHandler receives the query; `query.answer(results, ...)` accepts typed InlineQueryResult* objects. Use stable result IDs, bounded pagination and deliberate cache settings for personalized data. Rich inline results use InputRichMessageContent. ChosenInlineResultHandler observes selected results when Telegram delivers them; do not assume this is a guaranteed transaction receipt.

Source: `pyrogram/dispatcher.py`, `pyrogram/filters.py`, `pyrogram/handlers/`, `pyrogram/methods/decorators/`, `pyrogram/types/bots_and_keyboards/callback_query.py` at the [pinned commit](provenance.md).
