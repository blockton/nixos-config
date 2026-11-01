"""Offline contract tests against pinned Kurigram. No auth, sockets or sessions."""

import ast
import importlib.util
import inspect
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock
from pyrogram import Client, enums, filters, raw, types
from pyrogram.parser.parser import Parser
from pyrogram.methods.messages.edit_message_text import EditMessageText
import pyrogram

ROOT = Path(__file__).resolve().parents[1]


def asset(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "assets" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)

    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class FakeApp:
    def __init__(self):
        self.callbacks = []

    def on_message(self, *args, **kwargs):
        return self.decorator

    def on_callback_query(self, *args, **kwargs):
        return self.decorator

    def decorator(self, callback):
        self.callbacks.append(callback)
        return callback


class Contracts(unittest.IsolatedAsyncioTestCase):
    def test_version_and_signatures(self):
        self.assertEqual(pyrogram.__version__, "2.2.26")
        self.assertEqual(raw.all.layer, 229)
        self.assertNotIn(
            "business_connection_id",
            inspect.signature(Client.send_rich_message).parameters,
        )
        self.assertFalse(hasattr(Client, "stop_message_generation"))
        self.assertIn(
            "rich_message", inspect.signature(Client.edit_message_text).parameters
        )
        self.assertNotIn(
            "icon_custom_emoji_id",
            inspect.signature(types.RichMessageButton).parameters,
        )
        for method, args, kwargs in [
            (Client.send_message, (None, 123, "hi"), {}),
            (
                Client.edit_message_text,
                (None, 123, 1),
                {"rich_message": types.InputRichMessage(html="<p>x</p>")},
            ),
            (
                Client.send_rich_message_draft,
                (None, 123, 1, types.InputRichMessage(markdown="x")),
                {},
            ),
        ]:
            inspect.signature(method).bind(*args, **kwargs)

    async def test_basic_handler_and_filter(self):
        app = FakeApp()
        start = asset("minimal_bot").register(app)
        message = SimpleNamespace(reply_text=AsyncMock())
        await start(app, message)
        message.reply_text.assert_awaited_once_with("Ready.")
        msg = types.Message(
            id=1,
            text="/start",
            from_user=types.User(id=1, first_name="A"),
            chat=types.Chat(id=1, type=enums.ChatType.PRIVATE),
        )
        client = SimpleNamespace(
            me=types.User(id=99, first_name="Bot", username="sample_bot")
        )
        self.assertTrue(await (filters.private & filters.command("start"))(client, msg))
        self.assertEqual(msg.command, ["start"])

    async def test_rich_table_buttons_and_text(self):
        report = asset("rich_bot").build_report(3)
        result = await report.write(client=None)
        self.assertIsInstance(result, raw.types.InputRichMessage)
        table = result.blocks[1]
        self.assertIsInstance(table, raw.types.PageBlockTable)
        self.assertTrue(table.compact)
        self.assertEqual(table.rows[1].cells[1].text.text, "3")
        self.assertIsInstance(result.blocks[-1].buttons[0], raw.types.PageButton)
        self.assertEqual(result.blocks[-1].buttons[0].type.data, b"queue:refresh")
        label = asset("rich_bot").optional_emoji_label()
        button = types.RichMessageButton(text=label, callback_data="x")
        rich = await types.RichTextButton(button).write(None)
        self.assertEqual(rich.text.texts[0].document_id, 5875465628285931233)
        self.assertIsInstance(rich, raw.types.TextButton)

    async def test_invalid_rich_inputs(self):
        with self.assertRaises(ValueError):
            await types.InputRichMessage().write(client=None)
        with self.assertRaises(ValueError):
            await types.RichMessageButton(
                "bad", url="https://example.com", callback_data="x"
            ).write(None)
        with self.assertRaises(ValueError):
            await types.InputRichBlockSectionHeading("bad", 7).write(
                client=None, photos=[], documents=[]
            )

    async def test_formatting_emoji_and_offsets(self):
        text = "Status: 👍"
        entity = types.MessageEntity(
            type=enums.MessageEntityType.CUSTOM_EMOJI,
            offset=8,
            length=2,
            custom_emoji_id="5875465628285931233",
        )
        result = await entity.write()
        self.assertIsInstance(result, raw.types.MessageEntityCustomEmoji)
        self.assertEqual(result.document_id, 5875465628285931233)
        parsed = await Parser(None).parse(
            '<b>Ready</b> <tg-emoji emoji-id="5875465628285931233">👍</tg-emoji>',
            enums.ParseMode.HTML,
        )
        self.assertEqual(parsed["message"], "Ready 👍")
        self.assertEqual(parsed["entities"][-1].length, 2)
        self.assertEqual(len(text.encode("utf-16-le")) // 2, 10)

    async def test_callback_owner_duplicate_and_edit(self):
        app = FakeApp()
        task, complete = asset("callback_bot").register(app)
        message = SimpleNamespace(
            from_user=SimpleNamespace(id=123), reply_text=AsyncMock()
        )
        await task(app, message)
        markup = message.reply_text.await_args.kwargs["reply_markup"]
        payload = markup.inline_keyboard[0][0].callback_data
        query = SimpleNamespace(
            matches=[re.match(r"^task:([A-Za-z0-9_-]+)$", payload)],
            from_user=SimpleNamespace(id=999),
            answer=AsyncMock(),
            edit_message_text=AsyncMock(),
        )
        await complete(app, query)
        query.edit_message_text.assert_not_awaited()
        query.from_user.id = 123
        await complete(app, query)
        await complete(app, query)
        query.edit_message_text.assert_awaited_once_with("Completed.")

    async def test_rich_callback_edits_same_message(self):
        app = FakeApp()
        _, refresh = asset("rich_bot").register(app, AsyncMock(return_value=7))
        query = SimpleNamespace(
            message=SimpleNamespace(chat=SimpleNamespace(id=123)),
            from_user=SimpleNamespace(id=123),
            answer=AsyncMock(),
            edit_message_text=AsyncMock(),
        )
        await refresh(app, query)
        query.answer.assert_awaited_once()
        content = query.edit_message_text.await_args.kwargs["rich_message"]
        result = await content.write(client=None)
        self.assertEqual(result.blocks[1].rows[1].cells[1].text.text, "7")

    async def test_edit_entity_reset_is_real(self):
        fake = SimpleNamespace(
            link_preview_options=None,
            resolve_peer=AsyncMock(return_value=raw.types.InputPeerSelf()),
            parser=Parser(None),
            invoke=AsyncMock(side_effect=RuntimeError("captured")),
        )
        original = [
            types.MessageEntity(type=enums.MessageEntityType.BOLD, offset=0, length=1)
        ]
        with self.assertRaisesRegex(RuntimeError, "captured"):
            await EditMessageText.edit_message_text(
                fake,
                123,
                1,
                text="x",
                entities=original,
                parse_mode=enums.ParseMode.DISABLED,
            )
        self.assertIsNone(fake.invoke.await_args.args[0].entities)

    def test_inventory_access_and_declared_exports(self):
        data = json.loads((ROOT / "references/api-index.json").read_text())
        indexed = {e["access"] for e in data["entries"]}
        for entry in data["entries"]:
            obj = pyrogram
            for part in entry["access"].split(".")[1:]:
                obj = getattr(obj, part)
            if entry["signature"]:
                self.assertTrue(
                    callable(obj) or isinstance(obj, property), entry["access"]
                )
        for module in (pyrogram, types, enums, pyrogram.handlers, filters):
            for name in getattr(module, "__all__", []):
                if not inspect.ismodule(getattr(module, name)):
                    self.assertIn(module.__name__ + "." + name, indexed)

    def test_documented_python_blocks_compile(self):
        for path in ROOT.rglob("*.md"):
            for block in re.findall(r"```python\n(.*?)```", path.read_text(), re.S):
                compile(block, str(path), "exec")

    def test_inventory_cli_and_errors(self):
        import subprocess

        script = str(ROOT / "scripts/api_inventory.py")
        result = subprocess.run(
            [sys.executable, script, "RichMessageButton", "--limit", "2"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "RichMessageButton", json.loads(result.stdout.splitlines()[0])["access"]
        )
        bad = subprocess.run(
            [sys.executable, script, "--limit", "0"], capture_output=True, text=True
        )
        self.assertEqual(bad.returncode, 2)
        absent = subprocess.run(
            [sys.executable, script, "--index", "/nonexistent/kurigram-index.json"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(absent.returncode, 1)
        self.assertIn("api_inventory:", absent.stderr)

    def test_links_and_python_syntax(self):
        for path in ROOT.rglob("*.py"):
            ast.parse(path.read_text(), filename=str(path))
        for path in ROOT.rglob("*.md"):
            for link in re.findall(r"\]\(([^)]+)\)", path.read_text()):
                if "://" not in link and not link.startswith("#"):
                    self.assertTrue(
                        (path.parent / link.split("#")[0]).exists(), f"{path}: {link}"
                    )
        data = json.loads((ROOT / "references/api-index.json").read_text())
        self.assertEqual(
            len(data["entries"]), len({e["access"] for e in data["entries"]})
        )
        for entry in data["entries"]:
            self.assertTrue((ROOT / "references" / entry["reference"]).exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
