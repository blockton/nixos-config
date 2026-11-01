# Raw MTProto, RPC errors, rate control and debugging

Read the [inventory guide](api-inventory.md) to find all generated raw functions/types/base types, public errors and their hierarchy. Kurigram 2.2.26 compiles MTProto layer 229 from compiler/api/source/*.tl and generated errors from compiler/errors/source tables. A checkout does not necessarily contain generated modules until built; its wheel does.

## High-level/raw interoperation

```python
from pyrogram import raw

async def fetch_config(app):
    return await app.invoke(raw.functions.help.GetConfig())

async def raw_edit(app, chat_id, message_id, text, entities):
    peer = await app.resolve_peer(chat_id)
    return await app.invoke(raw.functions.messages.EditMessage(
        peer=peer, id=message_id, message=text, entities=entities,
    ))
```

raw_edit expects **raw** entity objects (e.g. `await high_level_entity.write()`), not MessageEntity instances. It returns raw Updates, not a high-level Message. Use the exact installed constructor: MTProto names and flags differ from HTTP Bot API parameters. Peer IDs are insufficient for most raw InputPeer values; resolve_peer acquires the right shape/access hash from storage/network. Unknown peers, wrong chat kinds or missing access hashes can fail even for a numerically correct ID. Do not manually fabricate access_hash=0 as a general solution.

`Client.invoke(query, retries=Session.MAX_RETRIES, timeout=Session.WAIT_TIMEOUT, sleep_threshold=None, retry_delay=Session.RETRY_DELAY, recaptcha_token=None, business_connection_id=None)` requires a connected client. It can wrap requests for business connections, reCAPTCHA, no_updates or takeout and refreshes cached peers from responses. Not every wrapped call has the same account eligibility. Generated constructors serialize flags and primitive types, not full semantic validation.

Inspect `pyrogram.raw.all.layer` and constructor signatures before adapting a current Telegram method. New protocol fields cannot be passed to an older generated class, and mixing generated modules from different layers is unsafe. Rebuild/update the whole pinned distribution deliberately. Protocol-only support is a candidate, not a guarantee of a safe fallback.

## Errors and named parameters

`from pyrogram.errors import FloodWait, RPCError, BadRequest, Forbidden` uses public re-exports. The generated hierarchy groups by RPC status; UnknownError and generic category fallbacks can represent server errors missing from the table. Never treat every BadRequest as a user mistake without examining RPC context.

Parameterized errors have `.value` plus a generated named property (e.g. FloodWait.seconds, migration dc_id when the class exposes it); use the actual indexed VALUE_NAME. Not every value is numeric: verification errors preserve string challenges. Named parameters may be None for malformed/unmatched server messages.

Session.invoke makes a bounded number of attempts. It catches FloodWait/FloodPremiumWait, reads `.seconds`, and rethrows if seconds is None or exceeds a nonnegative sleep_threshold. Otherwise it sleeps asynchronously then retries. A **negative threshold permits waits of any duration**; zero still permits a zero-second wait. Client defaults to 10 seconds. OSError/InternalServerError/ServiceUnavailable use retry_delay; exhaustion becomes TimeoutError. A response TimeoutError is not in that same retry catch tuple. Do not layer an unbounded retry loop over this machinery.

For a job queue, a long FloodWait should reschedule the job with its deadline rather than monopolize a handler. Example policy: configure sleep_threshold=0 to surface positive waits, record `e.seconds`, and allow the scheduler to retry a bounded number of times after that duration. Unknown seconds needs escalation/inspection, not arithmetic. Persist enough state to distinguish a not-attempted action from a timeout after possible acceptance.

A send timeout can mean “delivered but response lost.” Retrying a high-level send may choose a new random_id and duplicate it; use application idempotency/outbox reconciliation. The library reuses the same raw query within its own invoke attempts, but that is not global exactly-once delivery. Never blindly retry payments, moderation or other costly changes.

Unknown RPC handling can append `unknown_errors.txt` in the current directory; ensure deployment permissions and avoid collecting sensitive challenge material in shared logs. Log class/RPC/action identifiers with redaction; catch only expected errors at boundaries and preserve cancellation/tracebacks.

## Concurrency and cancellation

workers allow parallel handlers; locks protecting Python state must be application-owned. Avoid one global lock around all chats. Per-conversation ordering and a bounded outbound queue help rate control, but there is no fixed universal “safe messages/sec” for every account/chat/action. Paid broadcast flags do not bypass unrelated limits and spend Stars.

Retain background Task handles, cancel and await them on shutdown. Let asyncio.CancelledError propagate after cleanup. Use asyncio.timeout/wait_for at the service boundary only when the potential ambiguous RPC result is understood. Callback acknowledgements and message edits also consume network calls; coalesce progress updates.

## Diagnose by layer

- Missing symbol/keyword: inspect installed distribution and signature; eliminate the Pyrogram namespace collision before debugging Telegram.
- BotMethodInvalid/rights errors: check get_me identity, bot/user eligibility, chat type and current admin/business rights.
- PeerIdInvalid: inspect peer resolution/history/context, not only integer formatting.
- Session/database lock: inspect concurrent owners and writable persistent storage.
- FloodWait: inspect fanout, repeated edits, history scans and nested retry loops.
- Missing updates: inspect privacy mode, no_updates/skip_updates, handler class/group/filter ordering and callback context.
- Parser/entity failures: separate ordinary local parsing, Rich HTML server parsing and raw UTF-16 entity offsets.
- Clock/security/network failures: inspect system time, proxy normalization and transport; redact auth packets.

Source: `methods/advanced/invoke.py`, `session/session.py`, `errors/rpc_error.py`, `compiler/{api,errors}/`, `tests/unit/session/test_invoke_flood_wait.py`, error parameter tests; [pinned root](provenance.md). Telegram [MTProto](https://core.telegram.org/mtproto), [methods](https://core.telegram.org/methods) and [constructors](https://core.telegram.org/constructors) describe protocol behavior, not Python wrappers.
