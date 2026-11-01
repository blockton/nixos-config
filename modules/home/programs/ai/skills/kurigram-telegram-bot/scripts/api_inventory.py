"""Build/query an offline source-aware Kurigram API index; never starts a Client."""

from __future__ import annotations
import argparse
import ast
from collections import Counter
import importlib
import inspect
import json
from pathlib import Path
import pkgutil
import re
import sys
import subprocess

PIN = "2.2.26"
SHA = "b616bcebe4f54c7d90824d1a2517c070fd454fe5"
BASE = f"https://github.com/kurigram-org/kurigram/blob/{SHA}/"
ROOT = Path(__file__).resolve().parents[1]


def reference(path, name):
    if "rich" in path.lower() or "Rich" in name:
        return "rich-messages.md"
    if "/raw/" in path or "/errors/" in path:
        return "raw-errors-performance.md"
    if any(x in path for x in ("/handlers/", "filters.py", "/decorators/")):
        return "handlers-interactions.md"
    if any(
        x in path
        for x in (
            "/payments/",
            "/business/",
            "/stories/",
            "/premium/",
            "/bots/",
            "/chats/",
            "/invite_links/",
            "/users/",
            "/contacts/",
            "/folders/",
            "/phone/",
        )
    ):
        return "capabilities.md"
    if any(
        x in name.lower()
        for x in (
            "media",
            "photo",
            "video",
            "audio",
            "document",
            "sticker",
            "download",
            "upload",
            "file",
            "animation",
            "voice",
        )
    ):
        return "media.md"
    if "/messages/" in path or "/messages_and_media/" in path:
        return "messaging-formatting.md"
    return "lifecycle-production.md"


def build(checkout):
    import pyrogram
    from pyrogram import Client, enums, filters, handlers, types, raw, errors

    if pyrogram.__version__ != PIN:
        raise ValueError(f"Expected Kurigram {PIN}; found {pyrogram.__version__}")
    if (
        subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=checkout, text=True
        ).strip()
        != SHA
    ):
        raise ValueError("Source checkout does not match pinned commit")
    package = Path(pyrogram.__file__).resolve().parent
    schema_ids = {}
    schema_bases = {}
    for schema in sorted((checkout / "compiler/api/source").glob("*.tl")):
        for line_no, text in enumerate(schema.read_text().splitlines(), 1):
            match = re.match(r"([\w.]+)#([0-9a-f]+).*?=\s*([\w.]+)", text)
            if match:
                loc = (schema.relative_to(checkout).as_posix(), line_no)
                schema_ids[int(match[2], 16)] = loc
                schema_bases.setdefault(
                    match[3].split(".")[-1].replace("_", "").lower(), loc
                )
    error_ids = {}
    error_codes = {}
    for table in sorted((checkout / "compiler/errors/source").glob("*.tsv")):
        loc = table.relative_to(checkout).as_posix()
        error_codes[int(table.name.split("_")[0])] = (loc, 1)
        for line_no, text in enumerate(table.read_text().splitlines(), 1):
            error_ids[text.split("\t")[0]] = (loc, line_no)
    entries = {}
    missing = []

    def add(access, obj, kind, owner=None):
        target = inspect.unwrap(
            type(obj).__call__
            if isinstance(obj, filters.Filter)
            else obj.fget
            if isinstance(obj, property)
            else obj
        )
        try:
            file = Path(
                inspect.getsourcefile(target) or inspect.getsourcefile(type(obj))
            ).resolve()
            rel = "pyrogram/" + file.relative_to(package).as_posix()
            line = inspect.getsourcelines(target)[1]
        except (TypeError, ValueError, OSError):
            rel, line = owner or "pyrogram/__init__.py", 1
            missing.append(
                {
                    "access": access,
                    "issue": "No exact source anchor; package root fallback",
                }
            )
        generated = rel.startswith(
            (
                "pyrogram/raw/functions/",
                "pyrogram/raw/types/",
                "pyrogram/raw/base/",
                "pyrogram/errors/exceptions/",
            )
        )
        if generated:
            identifier = getattr(obj, "ID", None)
            if kind == "raw-base":
                rel, line = schema_bases.get(
                    getattr(obj, "__name__", "").lower(),
                    ("compiler/api/source/main_api.tl", 1),
                )
            elif isinstance(identifier, int):
                rel, line = schema_ids.get(
                    identifier, ("compiler/api/source/main_api.tl", 1)
                )
            else:
                rel, line = error_ids.get(
                    identifier,
                    error_codes.get(
                        getattr(obj, "CODE", None), ("compiler/errors/compiler.py", 1)
                    ),
                )
        try:
            signature = str(inspect.signature(target))
            signature = re.sub(r"0x[0-9a-fA-F]+", "0xADDRESS", signature)
            signature = re.sub(r"PosixPath\('/[^']*'\)", "PosixPath('<cwd>')", signature)
        except (TypeError, ValueError):
            signature = None
        doc = inspect.getdoc(target) or ""
        entry = dict(
            access=access,
            kind=kind,
            signature=signature,
            source=BASE + rel + f"#L{line}",
            module=getattr(target, "__module__", None),
            reference=reference(rel, access),
            verification="import+signature" if signature else "import",
            account_hint=(
                "users-bots"
                if "usable-by/users-bots" in doc
                else "bots"
                if "usable-by/bots." in doc
                else "users"
                if "usable-by/users." in doc
                else "not-specified"
            ),
            constraints="See pinned source docstring and implementation; availability is not authorization.",
        )
        if inspect.isclass(obj):
            entry["bases"] = [x.__module__ + "." + x.__name__ for x in obj.__bases__]
            if issubclass(obj, enums.ParseMode.__bases__[0]):
                entry["members"] = {
                    k: str(v.value) for k, v in getattr(obj, "__members__", {}).items()
                }
            for attr in ("CODE", "ID", "VALUE_NAME"):
                if hasattr(obj, attr):
                    entry[attr] = getattr(obj, attr)
            try:
                tree = ast.parse(inspect.getsource(obj))
                entry["attributes"] = sorted(
                    {
                        n.attr
                        for n in ast.walk(tree)
                        if isinstance(n, ast.Attribute)
                        and isinstance(n.value, ast.Name)
                        and n.value.id == "self"
                        and isinstance(n.ctx, ast.Store)
                        and not n.attr.startswith("_")
                    }
                )
                entry["overloads"] = [
                    ast.unparse(n.args)
                    for n in ast.walk(tree)
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and any(
                        ast.unparse(d).endswith("overload") for d in n.decorator_list
                    )
                ]
            except (OSError, TypeError, IndentationError, SyntaxError):
                pass
        if signature:
            # Overloads can sit above the implementation and are not returned by inspect.
            source_file = (
                package.parent
                / (
                    "pyrogram/"
                    + Path(inspect.getsourcefile(inspect.unwrap(target)))
                    .relative_to(package)
                    .as_posix()
                )
                if inspect.isfunction(target)
                else None
            )
            if source_file is not None:
                tree = ast.parse(source_file.read_text())
                overloads = [
                    ast.unparse(n.args)
                    + (" -> " + ast.unparse(n.returns) if n.returns else "")
                    for n in ast.walk(tree)
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and n.name == target.__name__
                    and any(
                        ast.unparse(d).endswith("overload") for d in n.decorator_list
                    )
                ]
                if overloads:
                    entry["overloads"] = overloads
        source_path = checkout / rel
        if not source_path.is_file() or line > len(
            source_path.read_text().splitlines()
        ):
            raise ValueError(f"Invalid pinned source anchor: {access}: {rel}:{line}")
        entries[access] = entry

    for module in (pyrogram, types, enums, handlers, filters, errors):
        names = getattr(module, "__all__", None) or [
            n for n in vars(module) if not n.startswith("_")
        ]
        for name in names:
            obj = getattr(module, name)
            if inspect.ismodule(obj):
                continue
            if getattr(obj, "__module__", "").startswith("pyrogram") or isinstance(
                obj, filters.Filter
            ):
                access = module.__name__ + "." + name
                add(
                    access,
                    obj,
                    "class"
                    if inspect.isclass(obj)
                    else "function"
                    if callable(obj) and not isinstance(obj, filters.Filter)
                    else "filter",
                )
                if inspect.isclass(obj) and module in (types, handlers):
                    for member, value in vars(obj).items():
                        if not member.startswith("_") and (
                            inspect.isfunction(value)
                            or isinstance(value, (property, staticmethod, classmethod))
                        ):
                            add(
                                access + "." + member,
                                getattr(obj, member),
                                "property"
                                if isinstance(value, property)
                                else "bound-method",
                            )
    add("pyrogram.Client", Client, "class")
    for name in dir(Client):
        if not name.startswith("_"):
            value = getattr(Client, name)
            if callable(value) or isinstance(value, property):
                add("pyrogram.Client." + name, value, "client-method")
    for namespace in (raw.functions, raw.types, raw.base):
        for info in pkgutil.walk_packages(namespace.__path__, namespace.__name__ + "."):
            module = importlib.import_module(info.name)
            for name, obj in vars(module).items():
                if (
                    inspect.isclass(obj)
                    and obj.__module__ == module.__name__
                    and not name.startswith("_")
                ):
                    suffix = module.__name__[len(namespace.__name__) + 1 :].split(".")[
                        :-1
                    ]
                    access = ".".join([namespace.__name__, *suffix, name])
                    add(
                        access,
                        obj,
                        "raw-function"
                        if namespace is raw.functions
                        else "raw-base"
                        if namespace is raw.base
                        else "raw-type",
                    )
    return dict(
        version=PIN,
        tag="v" + PIN,
        commit=SHA,
        layer=raw.all.layer,
        source_commit_verified=True,
        scope="Root exports; Client public callables; exported types, attributes and direct bound methods; enums/members; handlers; filters; RPC errors; generated raw functions/types/base. Private helpers and arbitrary internal modules excluded.",
        gaps=missing,
        counts=dict(Counter(e["kind"] for e in entries.values())),
        entries=sorted(entries.values(), key=lambda e: e["access"]),
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", nargs="?", default="")
    parser.add_argument(
        "--build", type=Path, help="Write an index using installed pinned release"
    )
    parser.add_argument(
        "--source-checkout",
        type=Path,
        help="Pinned git checkout, required with --build",
    )
    parser.add_argument(
        "--index", type=Path, default=ROOT / "references/api-index.json"
    )
    parser.add_argument("--limit", type=int, default=30)
    args = parser.parse_args()
    if args.limit < 1:
        parser.error("--limit must be positive")
    if args.build:
        if args.source_checkout is None:
            parser.error("--build requires --source-checkout")
        result = build(args.source_checkout)
        args.build.write_text(json.dumps(result, default=str, indent=2) + "\n")
        print(json.dumps(result["counts"]))
        return
    data = json.loads(args.index.read_text())
    found = [
        e for e in data["entries"] if args.query.casefold() in e["access"].casefold()
    ]
    for entry in found[: args.limit]:
        print(json.dumps(entry))
    print(
        f"{len(found)} matches; displayed {min(len(found), args.limit)}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, ImportError, subprocess.CalledProcessError) as exc:
        print(f"api_inventory: {exc}", file=sys.stderr)
        sys.exit(1)
