# Pinned source and verification record

## Release selection

Researched on 2026-11-01. GitHub's authoritative [latest stable release endpoint](https://api.github.com/repos/kurigram-org/kurigram/releases/latest) selected **v2.2.26**, published 2026-09-12T17:45:26Z. [Release notes](https://github.com/kurigram-org/kurigram/releases/tag/v2.2.26) were inspected; no development-branch behavior is presented as stable.

- Distribution/version: Kurigram 2.2.26; import namespace pyrogram.
- Annotated tag object: 9d03c17962ecfc02c877cd7a6320769318c0c00a.
- Peeled commit: **b616bcebe4f54c7d90824d1a2517c070fd454fe5**.
- [Pinned source root](https://github.com/kurigram-org/kurigram/tree/b616bcebe4f54c7d90824d1a2517c070fd454fe5).
- MTProto schema layer: **229**, compiler/api/source/main_api.tl.
- Source package was built into an isolated environment for introspection/tests; Python 3.13.15. Metadata requires Python >=3.10.

GitHub's latest endpoint reported target_commitish=dev; that branch name was not used as the source pin. The exact stable tag was cloned and its peeled commit checked instead. This record establishes tag/source behavior, not byte-for-byte equivalence with a separately downloaded PyPI wheel.

## Investigation map

Inspected package metadata/build hook and version exports; Client constructor/storage/auth/sync wrappers; public method packages and source signatures; exported types/enums/handlers/filters/errors; dispatcher parsing, group propagation/error handling; invoke/session retries/shutdown; proxy normalization/transports; file IDs/upload/download/streaming; ordinary HTML/Markdown parsers; rich input/received blocks/text/buttons/media and send/edit/draft/ephemeral pathways; generated raw functions/types/base schema and compiler/error tables; regression tests and release notes.

All included API surfaces were programmatically enumerated and import/signature indexed. Focused implementation reading covered the complex workflows described in prose; this is not a claim that every line of every generated constructor was manually reviewed. Per-entry links locate exact pinned implementations or schema definitions. The reference set is original engineering guidance and short original examples, not a redistributed upstream manual/source dump.

Upstream source is LGPL-3.0-or-later; copyright/attribution: Pyrogram authors including Dan and Kurigram contributors. See upstream [COPYING.lesser](https://github.com/kurigram-org/kurigram/blob/b616bcebe4f54c7d90824d1a2517c070fd454fe5/COPYING.lesser) and NOTICE before copying implementation code. The inventory records API facts, paths and signatures; the skill does not vendor the library.

## External documentation and limitations

The [homepage](https://kurigram.icu) confirms stable installation and links the official docs. [Hosted docs](https://docs.kurigram.icu) returned an Anubis access-denied page during research, so pinned source docstrings, compiler materials and tests were the library evidence. The supplied Telegram /constructor URL returned 404; use [constructors](https://core.telegram.org/constructors) and specific constructor links instead.

Telegram [Bot API and rich grammar](https://core.telegram.org/bots/api#rich-message-formatting-options), [changelog](https://core.telegram.org/bots/api-changelog), [MTProto](https://core.telegram.org/mtproto) and [method catalog](https://core.telegram.org/methods) were consulted as protocol references. HTTP Bot API fields are not treated as evidence of high-level Kurigram support. Rich HTML/Markdown is server-parsed; these grammars were not live exercised. No minimum client version, universal account entitlement or fixture emoji availability was established.

## Verification results

- Upstream pinned unit and guard suite: **846 passed**, one warning, no Telegram integration tests selected. An initial sandbox run stopped on loopback socket-binding failures; rerunning with local socket permission passed.
- Custom skill contract suite: **12 passed**. All Python examples/snippets compile; imports, core signatures, real serializers, fake handler/callback paths, inventory resolution and declared export coverage checked. Ruff E9/F and formatter checks passed.
- API inventory: **5570 searchable entries**, including 427 public Client callables, 333 direct bound methods, 24 properties, 423 exported high-level types, 43 enums, 31 handlers and 952 error classes. Raw inventory includes 824 functions, 1692 types and 637 base types. Additional root/filter/helper exports account for remaining entries. Model fields, enum members and nine entries with overload metadata are nested. All entry access paths resolve; declared non-module exports are covered; every source path/line was checked against the pinned checkout with zero source-anchor gaps. This measures the stated inventory boundary, not universal semantic coverage.
- Independent agent forward test: four realistic tasks produced three implementation artifacts plus an offline test module; **4 tests passed**. It correctly identified absent high-level rich payment/generation APIs and used explicit raw entity conversion for preservation. No live side effects.
- Syntax/import/signature/serialization: checked against a local build of the pinned source, without tokens or session strings.
- Live Telegram: **not tested**. Auth, server permission checks, monetary behavior, real uploads, client rendering, rate ceilings and HTML/Markdown server acceptance remain untested.

Material implementation caveats: rich send lacks business_connection_id/schedule_date; no public stop_message_generation/edit_rich_message/edit_table_cell; received rich trees are not lossless input trees; RichText TextImage/anchor distinctions are incomplete; ordinary edit_message_text resets explicit entities before parsing; some upstream draft/error-handler documentation disagrees with actual signatures/control flow. Focused references describe supported paths and avoid claiming nonexistent APIs.
