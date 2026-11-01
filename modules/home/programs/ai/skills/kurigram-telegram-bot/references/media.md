# Media, files and transfers

Search [API inventory](api-inventory.md) for send_photo/video/audio/voice/document/animation/sticker/video_note/live_photo, InputMedia*, download_media, stream_media and save_file. These are MTProto methods: HTTP Bot API file/upload limits are not interchangeable.

## Send and reuse

A send method commonly accepts a local str/Path, supported HTTP URL, Telegram file_id or binary stream; accepted forms differ per method. A file_unique_id identifies content but **cannot** be sent or downloaded. For in-memory uploads, give BytesIO a `.name` with a useful extension and keep it open until the await completes. Path support across local uploads was expanded in 2.2.26.

```python
from io import BytesIO

async def send_report(app, chat_id, content: bytes):
    document = BytesIO(content)
    document.name = "report.txt"
    return await app.send_document(chat_id, document, caption="Report")
```

Reuse a received object's file_id to avoid uploading again; do not assume file IDs work across bot identities. File references/access hashes may expire; refetch the source message/media in the same account before retrying. Explicitly set filename, MIME/streaming/duration/size metadata only when truthful; Telegram may infer or reject inconsistent metadata. Thumbnails and cover media have method-specific encoding/dimension rules and are not generic URL substitutions.

Use caption_entities or explicit caption parse mode for media formatting. Ordinary entities use UTF-16 offsets; optional custom emoji works through CUSTOM_EMOJI caption entities with the string fixture described in [formatting](messaging-formatting.md). Do not add it by default.

## Albums and rich media layouts

`send_media_group(chat_id, media=[InputMediaPhoto(...), ...]) -> list[Message]` sends an album, not a RichMessage. Usual album bounds documented by this method are 2–10 items; audio/document mixing has special constraints. Each InputMedia owns caption/entity fields; there is no single generic album caption argument. Media group IDs associate messages; keep all returned message IDs if later editing/deleting them. Bound copy_media_group/get_media_group have their own behavior.

Rich collage/slideshow/document/photo blocks belong to InputRichMessage and take InputMedia objects; see [rich media](rich-messages.md). Conversion can call messages.UploadMedia to acquire media identifiers. A reference key in rich HTML is not a file_id or media document ID.

## Download, streaming and progress

`download_media(message_or_file_id, file_name="downloads/", in_memory=False, block=True, progress=None, progress_args=())` returns a path, BinaryIO, lists for supported composite cases, or None. Do not assume success merely because no exception escaped; check the returned value. in_memory transfers allocate the whole result, so set an application size budget before downloading untrusted files. Do not trust supplied filenames as destination paths; choose a controlled directory and generated basename.

`stream_media(message, limit=0, offset=0)` is an **async generator of bytes**, consumed with `async for`. offset and limit are in approximately 1 MiB chunks, not bytes. Negative offsets require known file_size; a bare file ID cannot provide it. Consume incrementally to maintain backpressure. A consumer cancellation should close the generator and any owned file resources.

Progress callbacks receive `(current, total, *progress_args)`; both regular/async supported paths should be checked for the particular method. Throttle status-message edits in callbacks; they can dominate transfer cost and trigger FloodWait. `app.stop_transmission()` raises StopTransmission within a supported progress path; it is not the draft-generation stop mechanism. Handle the method's cancellation return separately from a successful path.

`max_concurrent_transmissions` defaults to one; increase only with measured bandwidth/memory and rate impact. Avoid shared binary stream cursors across simultaneous uploads. save_file now raises upload failures instead of only logging/hiding them in this release, so code relying on silent None needs review. Keep retries bounded and do not blindly resend media after an ambiguous send timeout.

Source: `methods/messages/{download_media,stream_media,send_media_group,send_document}.py`, `methods/advanced/save_file.py`, `types/input_content/input_media*.py`, `file_id.py`; upstream transfer and Path regression tests. All at [pinned provenance](provenance.md).
