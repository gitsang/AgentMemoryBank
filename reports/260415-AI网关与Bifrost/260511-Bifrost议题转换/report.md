# Bifrost issue search: chat / responses / messages conversion

Date: 2026-05-11
Target repo: https://github.com/maximhq/bifrost/issues
Question: whether someone already asked the same problem that Bifrost seems to only support converting Chat/Chat Completions to Responses, rather than arbitrary conversion among chat, responses, and messages.

## Conclusion

I did not find an issue that states the exact broad request: "support arbitrary conversion among chat, responses, and messages".

I did find close matches:

1. #2826, open: `[Bug]: openai compatible models from opencode go fails when running through claude code`
   - URL: https://github.com/maximhq/bifrost/issues/2826
   - Most directly relevant to the reverse direction problem.
   - The reporter uses a provider that only exposes `/v1/chat/completions`, overrides `responses` and `responses_stream` to `/v1/chat/completions`, and says converting `Responses` / `ResponsesStream` functions to `chatResponse` / `ChatCompletionStream` fixed the issue locally.
   - This is not framed as arbitrary chat/responses/messages conversion, but it is effectively a Responses -> Chat Completions fallback/conversion gap.

2. #2635, open: `n8n Chat Model node incompatible — Responses API not proxied correctly`
   - URL: https://github.com/maximhq/bifrost/issues/2635
   - Expected behavior explicitly says Bifrost should proxy `/v1/responses` correctly or gracefully fall back to `/v1/chat/completions`.
   - Related to Responses -> Chat fallback, not arbitrary three-format conversion.

3. PR #2599, open: `fix: add responses to chat fallback for custom openai providers`
   - URL: https://github.com/maximhq/bifrost/pull/2599
   - Direct implementation attempt for Responses -> Chat Completions fallback for OpenAI-compatible providers without `/v1/responses`.
   - Body says it reuses `ToChatRequest()` and `ToBifrostResponsesResponse()` and adds fallback in `OpenAIProvider.Responses()` / `ResponsesStream()`.
   - CodeRabbit summary describes bidirectional request/response conversion preserving user/format intent and streaming support.
   - Because it is still open, the capability may not be released/merged.

4. #426, closed: `[Feature]: Add support for OpenAI responses API`
   - URL: https://github.com/maximhq/bifrost/issues/426
   - Original feature request for supporting both `chatCompletion` and `responses` formats for OpenAI providers.
   - Closed as released in a prerelease, but it is about adding Responses API support, not arbitrary conversion.

5. #1976 and #1977, closed: Chat-to-Responses mux conversion bugs
   - #1976: https://github.com/maximhq/bifrost/issues/1976
   - #1977: https://github.com/maximhq/bifrost/issues/1977
   - These confirm existing Chat -> Responses mux/conversion paths had specific fidelity bugs.
   - They do not ask for reverse or arbitrary conversion.

6. #3362, open: MCP/tool payload ordering and prompt cache misses
   - URL: https://github.com/maximhq/bifrost/issues/3362
   - Mentions config flags such as `convert_text_to_chat` and `convert_chat_to_responses`, but the issue itself is about deterministic tool ordering and prompt cache misses, not conversion support.

## Searches performed

Direct GitHub issue searches included:

- `chat to responses`
- `responses to chat`
- `convert responses to chat`
- `convert chat to responses`
- `messages conversion`
- `OpenAI Responses API conversion`
- `Anthropic messages responses`
- `anthropic messages chat responses conversion`
- `messages to chat completions`
- `messages to responses`
- `only supports convert_chat_to_responses`
- `chat responses messages arbitrary`
- `convert_text_to_chat convert_chat_to_responses`
- `messages endpoint responses fallback chat completions`

Web searches included:

- `site:github.com/maximhq/bifrost/issues Bifrost "chat to responses" "convert"`
- `site:github.com/maximhq/bifrost/issues maximhq bifrost "responses to chat"`
- `site:github.com/maximhq/bifrost/issues maximhq bifrost "messages" "Responses API" "Chat Completions"`

Local workspace search included:

- `bifrost`
- `maximhq`
- `chat to responses`
- `responses to chat`
- `messages conversion`
- `convert chat`

Local context found only prior gateway architecture notes about normalizing `/responses`, `/messages`, and `/chat/completions` into a unified internal structure; no prior local note about this exact upstream issue.

## Practical answer

If opening/commenting an issue, the strongest existing place to reference is #2826 for the concrete failure and PR #2599 for the proposed implementation. If the desired request is broader than Responses -> Chat fallback, a new issue may still be appropriate, but it should cite #2826, #2635, and #2599 to avoid looking like a duplicate.
