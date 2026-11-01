# Examples and offline verification

Examples are optional starting points, not mandatory project templates. They use the real Kurigram namespace and pin described in [provenance](provenance.md). No included test authenticates or calls Telegram.

## Run examples deliberately

```sh
uv init --python 3.13 example-bot
cd example-bot
uv add 'kurigram==2.2.26'
# Copy one selected example from this skill's assets directory to bot.py.
# Supply API_ID, API_HASH and BOT_TOKEN through your secret mechanism.
uv run python bot.py
```

- [minimal_bot.py](../assets/minimal_bot.py): basic private /start handler, async context lifecycle.
- [callback_bot.py](../assets/callback_bot.py): /task with an opaque expiring owner-bound token, early acknowledgement, serialized duplicate suppression and an edit of the current message. In-memory state disappears on restart; production durability requires a database transaction/outbox. Its “service operation” is intentionally a local state transition. Telegram edit failure after completion does not roll it back.
- [rich_bot.py](../assets/rich_bot.py): /queue with an actual compact table, disclosure and styled rich callback button; refresh rebuilds/edits the same message. A supplied get_count service isolates domain data. An optional custom emoji label function is unused by default.

To grow modularly, move build_report into a presentation module, get_count into a service, persistence into a repository, and register(app, service) into a handler module. Preserve dependency direction and async lifecycle ownership; do not split a tiny bot merely to mirror this layout.

## What the checks establish

```sh
uv run --with 'kurigram==2.2.26' python /absolute/path/to/skill/scripts/verify_offline.py
python /absolute/path/to/skill/scripts/api_inventory.py RichTextButton
```

The verification script checks pinned imports/signatures/layer, handler execution using fake adapters, real command/private filter selection, owner rejection and duplicate callback behavior, same-message rich edit invocation, rich table/button/custom emoji serialization, invalid-input rejection, local HTML entity offsets, the source-derived edit entity-reset bug, local links and Python syntax. It does not prove Telegram rendering, server grammar, auth, entitlement or RPC behavior over a live connection.

For application tests, fake transport-facing service methods with AsyncMock and test observable calls/state transitions. Test user/chat identity, invalid/stale callback data, missing message context, concurrent actions, exact edit-versus-send behavior and meaningful error outcomes. Keep parsing/formatting builders pure when possible. Use an isolated test database for transaction/idempotency tests. Do not invent a Mock method to conceal that the real Client lacks it: bind intended calls against inspect.signature and import real constructors.

Integration testing is optional and needs separately authorized credentials/chat targets. Test with a dedicated bot/session and explicit scope. Keep live tests opt-in and never run purchases, paid broadcasts or moderation actions merely to improve coverage. Mark verified syntax, imports, signatures, unit behavior and live behavior separately in reports.
