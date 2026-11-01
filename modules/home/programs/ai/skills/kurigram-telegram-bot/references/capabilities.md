# Account capabilities and feature domains

The [machine-readable index](api-inventory.md) is the full discoverable symbol surface. This page is a task-oriented map, not a promise that each method works for a bot. An account_hint is taken from the pinned docstring and can be stale. Verify the RPC, account identity, permissions, chat type and server capabilities before implementation. Raw availability does not remove restrictions.

## Chats, administration and topics

| Task | Stable high-level APIs | Conditions / result considerations |
| --- | --- | --- |
| Inspect chats/members | get_chat, get_chat_member, get_chat_members, get_chat_members_count | Member iteration is async; visibility and rights vary |
| Moderate | ban_chat_member, unban_chat_member, restrict_chat_member, promote_chat_member | Admin rights and applicable chat type; ChatPermissions differs from ChatPrivileges |
| Configure | set_chat_title, set_chat_description, set_chat_photo, set_chat_permissions, set_slow_mode, set_chat_protected_content | Role/right restrictions; partial permissions semantics need source review |
| Invitations | create_chat_invite_link, edit_chat_invite_link, revoke_chat_invite_link, approve_chat_join_request, decline_chat_join_request | Invite ownership, join-request state and admin rights |
| Forums | create_forum_topic, edit_forum_topic, close_forum_topic, reopen_forum_topic, delete_forum_topic | Forum eligibility and manage-topic/delete rights; use actual topic identifiers |
| Forum queries/pins | get_forum_topics, get_forum_topics_by_id, pin_forum_topic, unpin_forum_topic | These are marked users-only in pinned docs, despite bot-capable mutations elsewhere |
| Channel direct messages | get_direct_messages_topics, get_direct_messages_topics_by_id, set_chat_direct_messages_group | Separate DirectMessagesTopic routing; not a forum topic |
| History/dialogs/folders | get_chat_history, get_dialogs, search_messages, create_folder/get_folders | Many are user-account operations; do not build a bot backfill around unrestricted history access |

A posted message can identify sender_chat instead of from_user. Anonymous administrators and channel posts are not ordinary user accounts. Bot group privacy mode affects delivery; filters cannot recover updates Telegram never sends. Rights may change after a cached check, so handle RPC permission failures at the mutation boundary.

For a moderation workflow, verify the caller's authority, the bot's current privilege, the target's identity and chat context separately. Do not expose a destructive admin command merely because the bot itself has rights. Update handlers for members/join requests are distinct from service-message filters.

## Business, bots and guest interactions

get_business_connection returns BusinessConnection and rights metadata. BusinessConnectionHandler and dedicated business message handlers receive separate updates. send_message and several media/edit methods expose business_connection_id; Client.invoke wraps such calls in InvokeWithBusinessConnection and chooses the relevant session. Stable send_rich_message lacks that keyword: an HTTP Bot API business-rich field is not automatically available high-level here.

get_business_account_gifts, get_business_account_star_balance, delete_business_messages and transfer_business_account_stars exist. Their docstring account labels and actual business rights differ; consult each method rather than generalizing from the package name. Business connection IDs are not chat IDs or auth tokens.

ManagedBotUpdatedHandler, GuestMessageHandler, create_bot and answer_guest_query are discoverable in this release. Treat bot-management and guest-query capability as specific authorized workflows; they do not imply arbitrary bot impersonation. Search the index for ManagedBot*, Guest* and bot permission types before wiring an update.

## Payments, Stars, paid content and gifts

send_invoice/create_invoice_link, answer_shipping_query, answer_pre_checkout_query, refund_star_payment and edit_user_star_subscription are exposed for bots. LabeledPrice and payment-related models live in pyrogram.types. Use exact signatures: currencies, provider tokens, subscription periods and amounts vary by invoice type. Keep integer minor-unit accounting or the required Stars units; do not use floats for transaction totals.

Validate inventory/order ownership and total/currency on checkout; an affirmative pre-checkout answer is not proof of payment. Fulfill after the successful payment/service data is verified and stored idempotently by Telegram charge identity. Handle refunds separately. Test the pinned edit_user_star_subscription mapping because the release includes a restore/cancellation regression fix.

send_paid_media and PurchasedPaidMediaHandler expose paid-content pathways, while get_stars_balance and gift methods expose other Stars operations. Paid broadcasts are an explicit opt-in spend flag, not a free throughput optimization. Do not enable purchases/broadcast charges without the current task authorizing them.

get_available_gifts, send_gift, get_chat_gifts, get_received_gifts, transfer_gift, upgrade_gift and convert_gift_to_stars exist with differing account/business restrictions. Collection, resale, auction, crafting and purchase-offer methods are also in the index, many marked users-only. Availability is per method and gift state; ownership, transfer cooldown, balance and rights are not inferred from symbol existence. No offline fixture validates a real purchase.

## Stories, polls, checklists and other features

Story APIs include send_story, get_stories/get_chat_stories, edit_story_caption/media/privacy, delete_stories, forward_story/copy_story and can_post_stories. Most story creation/edit APIs are users-only according to pinned docs. A bot receiving an ordinary story-related message is not permission to post as a user. can_post_stories is a capability check, not a universal entitlement grant.

send_poll/stop_poll and PollHandler support poll workflows; vote_poll, add_poll_option and delete_poll_option have user restrictions. Use InputPollOption and Poll-related models from the inventory, not dictionaries copied from an HTTP Bot API payload.

send_checklist and edit_message_checklist exist for users/bots in source labels; InputChecklist, InputChecklistTask and related types model content. add_checklist_tasks and mark_checklist_tasks_as_done are labeled users-only. Business/right/Premium conditions and task IDs still matter. Rich list checkboxes are presentation, not automatic checklist RPC actions.

Reaction, boost, Premium, collectible and direct-message topic models are indexed. send_live_photo has a distinct typed media path. translate_text, translate_message_text and summarize_message are exposed but labeled users-only: do not silently promise them in a bot command. Phone/folder/contact/account methods in the public Client are not necessarily bot APIs.

## Unsupported versus unverified

Verified absent high-level examples: Client.stop_message_generation, Client.edit_rich_message, Client.edit_table_cell and send_rich_message(business_connection_id=...). RichMessageButton does not offer pay or a separate icon_custom_emoji_id. Do not infer raw-only implementations for these without inspecting the pinned raw signature and protocol eligibility.

The raw schema contains more capabilities than the high-level wrappers, but constructing a raw object alone proves neither server acceptance nor bot eligibility. A feature not covered in prose is not necessarily absent: query the index first, then read its pinned implementation. Features requiring target-client rendering, actual account rights or monetary execution remain unverified live.

Source: `pyrogram/methods/{chats,invite_links,bots,business,payments,stories,users,contacts,folders,phone}/`, domain types and generated layer 229 bindings. See [provenance](provenance.md) and per-entry source anchors.
