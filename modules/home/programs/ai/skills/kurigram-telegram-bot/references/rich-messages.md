# Rich Messages: construction, formatting and real tables

Contents: representation and transport; structured text; complete input block families; tables; media; parsing and compatibility. For buttons, drafts, callback edits and ephemeral messages read [rich interactions](rich-interactions.md). Exact constructors, received classes and source anchors are searchable in the [API inventory](api-inventory.md).

## Representation and transport

```python
from pyrogram import types
content = types.InputRichMessage(blocks=[
    types.InputRichBlockSectionHeading(text="Build report", size=2),
    types.InputRichBlockParagraph(text=["Result: ", types.RichTextBold("ready")]),
])
# await app.send_rich_message(chat_id, rich_message=content)
# await app.edit_message_text(chat_id, message_id, rich_message=content)
```

InputRichMessage accepts `blocks=None, html=None, markdown=None, media=None, is_rtl=None, skip_entity_detection=None`. Choose **one nonempty** content representation. The writer uses truthiness and precedence blocks > HTML > Markdown, rather than validating exclusivity; empty content raises ValueError. Supplying multiple forms silently ignores some. No parse_mode is involved.

HTML/Markdown become raw InputRichMessageHTML/InputRichMessageMarkdown; the server parses them. Structured blocks become raw InputRichMessage carrying PageBlock objects and separate photo/document/user vectors. Mentioned users are resolved to InputUser objects with access hashes; an unknown peer can fail resolution. `skip_entity_detection` maps to noautolink; `is_rtl` maps to rtl.

`Client.send_rich_message(chat_id, rich_message, ...) -> Message | None` sends a new message. Stable optional parameters include disable_notification, message_thread_id, direct_messages_topic_id, ephemeral_message_parameters, effect_id, reply_parameters, protect_content, allow_paid_broadcast, suggested_post_parameters and reply_markup. **It lacks business_connection_id and schedule_date**, even though other sends and the HTTP Bot API can expose related capabilities. Do not forward those keywords to it.

`Message.reply_rich` and `answer_rich` create messages with bound context; they do not edit an existing message. Received content is `message.rich_message: RichMessage`, with `blocks: list[RichBlock]` and is_rtl. InputRichBlock and received RichBlock are separate hierarchies: received blocks generally have no public write conversion. Keep an application-owned InputRichMessage builder when repeated edits are needed.

## Rich text primitives

The high-level annotations say RichText, but the serializer also accepts a string or a list of strings/RichText objects. A string becomes TextPlain; a list becomes TextConcat; None becomes TextEmpty. Do not instantiate the abstract RichText base.

| Family | Actual types and significant arguments |
| --- | --- |
| Decorations | RichTextBold, Italic, Underline, Strikethrough, Spoiler, Subscript, Superscript, Marked, Code; each takes text |
| External links | RichTextUrl(text, url), RichTextEmailAddress(text, email_address), RichTextPhoneNumber(text, phone_number), RichTextBankCardNumber(text, bank_card_number) |
| Telegram references | RichTextMention(text, username), RichTextTextMention(text, user: User), RichTextHashtag(text, hashtag), RichTextCashtag(text, cashtag), RichTextBotCommand(text, bot_command) |
| Date/time | RichTextDateTime(text, date: datetime, date_time_format=None); uses Telegram format r or w?[dD]?[tT]? |
| Formula | RichTextMathematicalExpression(expression); raw source, not local math rendering |
| Embedded emoji | RichTextCustomEmoji(custom_emoji_id: str, alternative_text: str); writer casts ID to int |
| Navigation | RichTextAnchor(text, name), RichTextAnchorLink(text, anchor_name), RichTextReference(text, name), RichTextReferenceLink(text, reference_name) |
| Inline interactive control | RichTextButton(button: RichMessageButton); see [interactions](rich-interactions.md) |

Names abbreviated in the decorations row all have the `RichText` prefix. Nesting wrappers is supported by recursive serialization; this does not mean every nesting is legal in every context. In particular button labels permit only plain text, custom emoji and formatted date/time primitives. Use timezone-aware datetime values and verify desired timezone display in Telegram clients.

Optional custom emoji fixture: `types.RichTextCustomEmoji("5875465628285931233", "👍")` can be nested into paragraph, heading, list item, table-cell text or permitted button labels. This is the same single ID used in the ordinary formatting examples. No offsets are needed in structured RichText; the raw constructor is TextCustomEmoji(document_id=int(id), alt=...). Eligibility and client rendering remain server-dependent.

## Complete input block families

All classes below are exported from `pyrogram.types`. Defaults and type details are in api-index.json; constructors are summarized here to explain decisions. Common caption objects are `RichBlockCaption(text, credit=None)`.

| Class suffix after InputRichBlock | Constructor shape and behavior |
| --- | --- |
| Paragraph | text; ordinary rich inline content |
| SectionHeading | text, size; size 1–6, validated on serialization |
| Preformatted | text, language=None; missing language becomes empty raw string |
| Footer | text; a footer block |
| Divider | no arguments; structural divider |
| MathematicalExpression | expression; block LaTeX source |
| Anchor | name; named navigation destination |
| List | items: list[InputRichBlockListItem]; any item value/type selects ordered encoding |
| ListItem | blocks, has_checkbox=None, is_checked=None, value=None, type=None; item belongs in List, not a normal standalone block |
| BlockQuotation | blocks, credit=None; nested block quote |
| ExpandableBlockQuotation | text, credit=None; collapsed text quote |
| PullQuotation | text, credit=None; emphasized quotation |
| Collage / Slideshow | blocks, caption=None; composite media layouts |
| Table | cells, is_bordered=None, is_striped=None, is_compact=None, caption=None |
| Details | summary, blocks, is_open=None; disclosure with nested blocks |
| Map | location: Location, zoom=None, width=None, height=None, caption=None |
| Buttons | buttons: list[RichMessageButton], align=None; one row, see interactions |
| Animation | animation: InputMediaAnimation, caption=None |
| Audio | audio: InputMediaAudio, caption=None |
| Document | document: InputMediaDocument, caption=None |
| Photo | photo: InputMediaPhoto, caption=None |
| Video | video: InputMediaVideo, caption=None |
| VoiceNote | voice_note: InputMediaVoiceNote, caption=None |
| Thinking | text; draft placeholder, not a universal persistent block |

List labels use type "1", "a", "A", "i", "I" and optional numeric value. Checkbox flags do not automatically create interactive task-state mutations: application callbacks/state and dedicated checklist APIs are separate.

Map docs constrain width/height to 0–10000, their sum to at most 10000 and ratio to at most 20; omitted values serialize as zero. Do not assume the writer validates all these constraints. Collage/slideshow accept nested block objects in Python but this is not proof arbitrary block combinations are server-valid.

## Real tables, spans and updates

`InputRichBlockTable.cells` is a list of **rows**, each a list of RichBlockTableCell. No separate high-level row/column class exists. Each row serializes to raw PageTableRow; cells serialize to PageTableCell.

Cell signature: `RichBlockTableCell(text=None, is_header=None, colspan=None, rowspan=None, align=None, valign=None)`. Text supports inline RichText, including custom emoji; it does not take arbitrary blocks. align accepts left/center/right; valign top/middle/bottom. The serializer encodes center/right and middle/bottom flags; unrecognized values can silently behave like defaults, so validate inputs in application code.

```python
from pyrogram import types as t

def report_table(count: int):
    return t.InputRichBlockTable(
        cells=[
            [t.RichBlockTableCell("Queue", is_header=True),
             t.RichBlockTableCell("Jobs", is_header=True, align="right")],
            [t.RichBlockTableCell(t.RichTextBold("Ready")),
             t.RichBlockTableCell(str(count), align="right")],
            [t.RichBlockTableCell("Updated now", colspan=2, align="center")],
        ],
        is_bordered=True, is_striped=True, is_compact=True,
        caption="Current work",
    )
```

Spans are optional integer fields intended for values greater than one. `text=None` denotes an invisible cell. The writer neither calculates a grid nor checks overlapping spans/rectangularity. Model the layout deliberately, keep rows consistent with intended spans, and test merged-cell rendering with actual target clients; do not invent an automatic placeholder/overlap rule. The example uses an unambiguous final row spanning two columns. A table update rebuilds the InputRichMessage and calls edit_message_text(rich_message=...), preserving the chat/message identity; there is no high-level edit_table_cell RPC.

Rich table support includes compact styling in this stable release. It is distinct from Markdown in a normal send_message; Unicode box drawing is not a substitute for the rich table API.

## Rich HTML and Rich Markdown

Use `InputRichMessage(html=...)` or `(markdown=...)`. These strings are transported unparsed by Kurigram, so local import/serialization tests cannot validate server grammar. The [official grammar](https://core.telegram.org/bots/api#rich-message-formatting-options) is a protocol reference, not proof of any Python constructor. Stable source explicitly carries these representations.

HTML can express headings, paragraphs, lists, tables, figures, disclosures and Telegram-specific elements. Build dynamic content with html.escape. Rich Markdown supports GFM-like inline/block notation and supported rich HTML additions. Do not reuse ordinary Pyrogram Markdown escaping indiscriminately. A small original example:

```python
from html import escape
from pyrogram import types

def html_report(label: str):
    return types.InputRichMessage(html=(
        "<h2>Queue</h2><table bordered compact>"
        "<tr><th>State</th><th>Count</th></tr>"
        f"<tr><td>{escape(label)}</td><td>3</td></tr></table>"
    ))

markdown_report = types.InputRichMessage(markdown=(
    "## Queue\n\n| State | Count |\n| --- | ---: |\n| Ready | 3 |"
))
```

For less-common tags, rich buttons, escaping reserved delimiters, nested HTML/Markdown, references and math, follow the current linked grammar and prefer structured constructors when exact escaping is difficult. Rich parsing is server-side; accepted HTML is not arbitrary browser HTML/CSS. Do not promise client theme colors or layout widths.

## Choosing syntax and nesting deliberately

For ordinary send_message, the local Markdown grammar uses its own delimiters (for example double-underscore italic); Rich Markdown has GFM-like single-asterisk/underscore italic and double-asterisk/underscore bold. Formatting strings are therefore not portable between the two APIs. Structured RichText avoids delimiter escaping altogether.

A rich document can combine inline decoration wrappers with structural blocks. Paragraph/heading/footer text and table cells carry inline content; Details and BlockQuotation carry block lists. A media object belongs in a media block, not arbitrarily nested into inline text. Keep code/math source separate from generated prose and escape syntax around untrusted interpolated text. For formula inputs, distinguish RichTextMathematicalExpression from InputRichBlockMathematicalExpression rather than embedding a block in a text slot.

Navigation has two sides: a named anchor/reference definition and a link to that name. The writer exposes both AnchorLink and ReferenceLink but encodes them similarly; received parsing cannot reliably recover the distinction. Do not use received navigation class identity as a durable application discriminator.

When Rich HTML and Rich Markdown are mixed, do not assume Markdown expands inside every HTML container. For unusual combinations use explicit blocks or consult/test the server grammar. Attribute escaping, text escaping and Markdown delimiter escaping are separate operations. Dynamic labels containing a pipe/newline can change a Markdown table's structure: use RichBlockTableCell objects for those values.

## Media and compatibility

Structured media blocks take InputMedia* objects. Their write path reuses InputPhoto/InputDocument identifiers for file IDs or uploads/resolves new media via messages.UploadMedia. The final rich message carries attachment vectors; an ID alone without access hash/file reference is insufficient. Resolving external/local media can do network I/O before sending the message. A failed send does not mean no upload happened.

For HTML/Markdown references, map a local string key to `InputRichMessageMedia(id="cover", media=InputMediaPhoto(...))`, then reference `tg://photo?id=cover`. Document/video/audio references use corresponding schemes and typed InputMedia values. Keys are 1–64 characters from ASCII letters, digits, underscore/hyphen. These keys are not Telegram numeric media IDs. For inline-query content, prefer previously uploaded files; lack of chat context makes upload eligibility more constrained.

Received RichBlock parser can emit RichBlockUnsupported; RichText parser has unfinished TextImage support and cannot preserve every anchor/reference distinction. TextConcat parsing does not propagate all user/chat context in recursive calls. Do not round-trip received trees blindly. Retain input builders or inspect raw data when lossless preservation matters.

Documented protocol ceilings are 32768 text characters, 500 counted blocks (including nested structures/rows/items), nesting depth 16, 50 attachments and 20 table columns. They are server limits, not comprehensive local validation; count encoded/entity/layout content carefully and check current protocol details before boundary-sensitive work. Client-version availability and merged-layout rendering were not live verified.

Source: `types/input_content/{input_rich_message,input_rich_block,input_rich_message_media}.py`, `types/messages_and_media/{rich_text,rich_block,rich_message}.py`; regression tests under `tests/unit/types/input_content/` and `tests/unit/types/messages_and_media/test_rich_block.py`. See [provenance](provenance.md).
