---
name: kurigram-telegram-bot
description: Design, build, extend, debug, refactor, test, and maintain Python Telegram bots using Kurigram, including handlers, formatting, Rich Messages, media, and raw MTProto API usage. Use for Kurigram projects or explicit Kurigram questions; do not replace another chosen Telegram framework.
---

# Kurigram Telegram Bot Engineering

Use `kurigram` as the distribution and `pyrogram` as the import namespace. This skill targets stable **2.2.26**, MTProto layer **229**; inspect the target project's installed version before applying release-specific APIs. Source and audit details: [provenance](references/provenance.md).

## Select the relevant reference

| Task | Read |
| --- | --- |
| Find a symbol, constructor, overload, enum, raw type, account hint | [API inventory](references/api-inventory.md); query `scripts/api_inventory.py SYMBOL` |
| Install, authenticate, manage loops/sessions, deploy or structure a bot | [Lifecycle and production](references/lifecycle-production.md) |
| Select handlers/filters, handle callbacks/inline queries, stateful flows | [Handlers and interactions](references/handlers-interactions.md) |
| Ordinary text/captions, entities, edits, reactions, replies | [Messaging and formatting](references/messaging-formatting.md) |
| Rich Messages, blocks, real tables, Rich HTML/Markdown | [Rich Messages](references/rich-messages.md) |
| Rich buttons, callbacks, drafts, progressive and ephemeral interfaces | [Rich interactions](references/rich-interactions.md) |
| Upload/download, albums, file IDs, streaming | [Media](references/media.md) |
| Moderation, topics, business, payments, stories, gifts and other domains | [Capabilities](references/capabilities.md) |
| Raw invocation, RPC errors, flood control, performance/debugging | [Raw, errors and performance](references/raw-errors-performance.md) |
| Runnable starting points and offline verification | [Examples and testing](references/examples-testing.md) |

Read only the references needed for the task. The JSON index is for search, not wholesale context loading. Its coverage is a symbol inventory, not a claim that every behavior is documented or live tested.

## Implement with evidence

1. Check the project lockfile and `importlib.metadata.version("kurigram")`; do not install Pyrogram alongside Kurigram because both own `pyrogram`. Preserve the project's framework and scope.
2. Locate the exact symbol/signature in the inventory, then inspect installed source when version or behavior matters. Distinguish Telegram protocol support, high-level Kurigram support, raw-only support, and unverified/unavailable behavior. A Bot API field is not proof of a Kurigram argument.
3. Check bot versus user account, chat type, rights and server/client capabilities. `usable-by` inventory hints come from docstrings, not live entitlement checks. Raw calls do not bypass restrictions.
4. Use async handlers with explicit lifecycle ownership. Bound methods can have different arguments and return types from Client methods. Keep network work behind services when useful; authorize state changes from server-side state.
5. Verify imports, signatures, serialization and fake network boundaries before claiming correctness. State separately what was syntax/import/signature checked, unit tested, or live tested. No credentials or live Telegram actions are needed for local checks.

Do not automatically add Rich Messages, styled buttons or Custom Emoji to a project. The single emoji ID in optional examples is a fixture, not application configuration. Preserve received entities/content deliberately; high-level rich parsing is not a lossless universal codec.

For an absent API, report the exact missing symbol/argument. Offer a raw alternative only after confirming its constructor, serialization and account eligibility. Do not manufacture an equivalent from regular keyboards or text-art tables when actual rich content was requested.
