# Public API inventory and coverage

Use `python scripts/api_inventory.py RichMessageButton` from the skill directory. Queries need only Python's standard library; `--build` needs installed pinned Kurigram and the pinned source checkout. Prefer a narrow query rather than reading the entire [api-index.json](api-index.json).

```sh
python scripts/api_inventory.py pyrogram.Client.send_message --limit 5
python scripts/api_inventory.py InputRichBlock --limit 40
python scripts/api_inventory.py pyrogram.handlers --limit 40
python scripts/api_inventory.py pyrogram.errors.FloodWait
python scripts/api_inventory.py pyrogram.raw.functions.messages.EditMessage
```

The index records canonical access path, callable/constructor signature where introspection supports it, implementation module, pinned source anchor, kind, routed reference, account hint and verification status. Classes also record bases, instance attributes assigned in source, available overload signatures, enum members or RPC metadata where applicable. Attributes are source discoveries, not an assertion that every field is always populated. Methods' annotations can disagree with implementation; workflows explain demonstrated exceptions.

## Inventory boundary

Included: root non-module exports; public Client callables including inherited methods; all declared exports of types/enums/handlers; public pyrogram-defined filter functions/classes and filter objects; RPC error exports; direct public bound methods/properties of exported high-level types; generated raw functions/types/base categories. Enum members and model fields are nested in their class entry rather than duplicated as independent rows. Raw namespaces are expanded recursively, including namespaced functions/types.

Excluded: private helpers; arbitrary symbols in internal modules not exported through the stated surfaces; inherited standard-library methods on enum/set/Exception classes; every runtime-only Client instance field; protocol functionality absent from the compiled schema. Internal parser/network/storage behavior is covered through focused source references, not falsely labeled public Client API.

Generated raw Python and exception files are not tracked upstream. Their inventory source links point to the **pinned TL schema or error table**, rather than dead GitHub links to generated files. Constructor signatures come from the built release. Raw base source anchors locate a schema usage/definition, not a Python implementation file.

## Reading coverage honestly

The inventory makes the declared surface searchable; it is not 100% behavioral documentation. Common/error-prone workflows have curated prose and offline tests. Less-common payment, account, story and raw methods have signatures/source routes and domain guidance, but not exhaustive execution examples or live acceptance tests. `import+signature` means symbol discovery/introspection, not server acceptance. Docstring account hints are not runtime checks.

Build counts and explicit verification limitations are recorded in [provenance](provenance.md). Source-bound inventories should be refreshed after a deliberate version update, not silently rewritten against a development branch.

## Rebuild/audit

From an isolated environment containing the selected stable release:

```sh
python scripts/api_inventory.py --build /tmp/new-api-index.json --source-checkout /path/to/pinned-checkout
python scripts/verify_offline.py
```

The generator verifies installed version and checkout HEAD against its constants. When maintaining a new release, update the constants only after authoritative stable release discovery, review source/schema changes, inspect changed signatures and rerun tests before replacing the committed index. Compare entries by access path and signatures, not only total counts. Resolve each access path via attributes and audit declared exports against indexed entries. A zero-length gaps list is not evidence all semantics were tested.
