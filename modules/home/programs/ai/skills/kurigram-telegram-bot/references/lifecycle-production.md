# Lifecycle, authentication and production

Scope: Kurigram 2.2.26. Search `Client`, `start`, `stop`, `run`, `compose`, `export_session_string` in the [inventory](api-inventory.md). Exact constructor defaults for machine-dependent device names and worker counts vary by interpreter/host.

## Installation and credentials

```sh
uv init --python 3.13 my-bot
cd my-bot
uv add 'kurigram==2.2.26'
uv add --dev pytest pytest-asyncio ruff
uv run python bot.py
```

Python >=3.10 is required by this release. Core dependencies are pyaes>=1.2.0 and python-socks[asyncio]>=2.4.0. Optional `uv add 'kurigram[fast]==2.2.26'` adds TgCrypto>=1.2.2 and uvloop>=0.21.0 on Linux/macOS; speedups are optional and do not change the API. `kurigram[qrcode]` installs QR-login support for user authorization. `dev` and `docs` are upstream dependency groups, not published extras. Lock resolved dependencies and use `uv sync --locked` in deployment.

Obtain `api_id` and `api_hash` for MTProto; bots also use their BotFather token. A bot token does not switch this library to the HTTP Bot API. Read credentials from the project's secret mechanism. Treat SQLite session files, journal files, exported session strings, proxy credentials and authentication logs as secrets. Do not commit them.

## Lifecycle ownership

Construct the Client inside the async loop that owns it when integrating with asyncio:

```python
import asyncio
import os
from pyrogram import Client, idle

async def main():
    app = Client("bot", api_id=int(os.environ["API_ID"]),
                 api_hash=os.environ["API_HASH"], bot_token=os.environ["BOT_TOKEN"])
    async with app:
        await idle()

if __name__ == "__main__":
    asyncio.run(main())
```

`start()` connects, authorizes when necessary, initializes workers and returns the Client. Register handlers before starting. `stop()` terminates workers and disconnects; `stop(clear_handlers=False)` preserves registrations for intentional reuse. A second start/stop in the wrong state raises ConnectionError. The context manager owns cleanup, including exceptions in its body.

`app.run()` takes keyword-only `use_qr` and `except_ids`; **this release does not accept a coroutine positional argument**, unlike examples for older Pyrogram. It operates its own loop using run_until_complete; do not call it inside a running asyncio loop. `pyrogram.compose(clients, sequential=False)` runs multiple independently named clients; inspect its installed signature when customizing orchestration.

The sync adapter wraps async methods: a call in a running loop returns an awaitable; calls without a running loop can execute synchronously. Do not depend on this convenience in async services: always await API calls. Async-generator methods such as history/member iteration need `async for`.

Stopping/restarting or changing handlers from a worker can deadlock if it waits for that same worker's locks. `await app.stop(block=False)` schedules shutdown; allow the owning supervisor/main task to wait for full termination. Add/remove handler operations also schedule lock acquisition; do not treat them as synchronous registration barriers while workers run.

## Sessions and authentication

`Client("name", workdir=...)` uses persistent storage; choose a writable persistent directory with restrictive permissions. Give independent processes/clients separate session files. Sharing SQLite sessions between replicas risks locking and concurrent authorization problems. Use one update consumer per intended bot identity unless the application explicitly coordinates distributed handling.

`in_memory=True` discards storage after shutdown; `session_string=...` restores an exported authorization and implies memory storage in the client loading path. Export only after authorization with `await app.export_session_string()`. A restored session represents its original account: passing a different bot token does not replace an already-authorized identity. Verify `await app.get_me()` rather than trusting configuration labels.

User flows expose `send_code`, `sign_in`, `check_password`, QR authorization and session management. Handle two-factor authentication and invalid/expired codes explicitly. Interactive authorization is unsuitable for an unattended service startup. Bot startup should fail clearly on missing/invalid secrets rather than accidentally prompting for a phone number.

## Configuration and reconnects

`skip_updates=True` is the constructor default: recovery behavior differs when disabled. `no_updates=True` suppresses dispatch and wraps invocations without updates; inappropriate for an ordinary receiving bot. `workers` controls concurrent handler workers, not global account rate limits. `max_concurrent_transmissions` controls transfer slots. Cache/fetch options (`fetch_replies`, `fetch_topics`, `fetch_stories`, `fetch_stickers`) trade enrichment work for cost; measure before disabling needed context.

Proxy normalization accepts supported proxy dictionaries, URL strings and typed proxy objects. Ordinary example: `proxy={"scheme":"socks5", "hostname":"127.0.0.1", "port":1080}`. Stable 2.2.26 includes HTTP, SOCKS4/5, classic MTProxy including fake TLS, and WEB proxy transport. Their fields/secrets are not interchangeable: use `pyrogram/connection/proxy.py` and its tests for scheme-specific inputs. WEB rejects fake-TLS ee secrets. Do not invent a generic MTProxy URL format.

Session internals track network tasks and reconnect state; this release includes fixes to await stopped tasks and prevent queued restarts resurrecting stopped sessions. Let the library reconnect. Use a bounded process restart policy for terminal failures; repeated authorization failures need intervention.

## Application architecture and deployment (recommendations)

For a small bot a single module is fine. As state grows, keep handler adapters thin, business logic independently testable, and repositories/transactions separate from Telegram transport. Inject services through closures or explicit registration functions rather than mutating unrelated globals. Persist workflow identity, owner, expiry and version in a database when restarts matter.

Workers can handle two updates for one user concurrently. Use per-conversation synchronization in one process; database transactions/optimistic version checks across processes. Do not hold a database transaction open during Telegram calls. An outbox can coordinate durable intentions and retries; delivery can be ambiguous after a network timeout.

Run as a non-root service/container with a writable private session volume, locked dependencies and SIGTERM handling. Stop accepting new work, cancel/await owned background tasks, close database/HTTP pools and await Client cleanup. Protect blocking I/O with an appropriate executor; never block the event loop with time.sleep. Avoid logging message bodies, token-bearing URLs, raw auth packets or session strings. Monitor queue latency, RPC outcomes, FloodWait duration, transfer failures and restarts.

Source anchors: `pyrogram/client.py`, `pyrogram/sync.py`, `pyrogram/methods/utilities/{start,stop,run,compose}.py`, `pyrogram/storage/`, `pyrogram/session/session.py`, `pyrogram/connection/proxy.py`. All paths resolve under the pinned [source root](provenance.md).
