# Bifrost /models customization research

Date: 2026-05-11

Question: Can Bifrost expose one logical `/models` entry such as `deepseek-v4-pro` while routing/fallback uses provider-specific backends like `openrouter/deepseek-v4-pro`, `bailian/deepseek-v4-pro`, `deepseek/deepseek-v4-pro`?

Findings:

- Bifrost v1.5.0 includes model alias support.
  - Docs: https://docs.getbifrost.ai/providers/aliasing-models
  - Release: https://github.com/maximhq/bifrost/releases/tag/transports%2Fv1.5.0
  - Discussion: https://github.com/maximhq/bifrost/discussions/945
  - PR: https://github.com/maximhq/bifrost/pull/2355
- Aliases let applications send user-facing names and resolve them to provider-specific identifiers.
- Routing rules can also dynamically route `model == "deepseek-v4-pro"` to specific provider/model targets with fallbacks.
- `/v1/models` docs still define model IDs as `provider/model` format.
  - Docs: https://docs.getbifrost.ai/api-reference/models/list-available-models
  - OpenAI docs: https://docs.getbifrost.ai/api-reference/openai-integration/list-models-openai-format
- PR #2525 explicitly changed list-models to include raw model IDs alongside aliases, so aliasing does not fully hide provider-specific entries.
  - https://github.com/maximhq/bifrost/pull/2525
- VK-based filtering exists and can reduce visible models for a virtual key.
  - PR #1611: https://github.com/maximhq/bifrost/pull/1611
  - PR #3094: https://github.com/maximhq/bifrost/pull/3094
- Directly relevant requests/discussions:
  - #1058 asks for aliasing/renaming models and includes comments about influencing `/v1/models` so consumers see stable model names without provider prefixes: https://github.com/maximhq/bifrost/issues/1058
  - #2162 asks to advertise routing expressions/aliases as models because some apps only accept names returned from `/v1/models`: https://github.com/maximhq/bifrost/issues/2162

Conclusion:

Bifrost has partial native support via aliases, routing rules, and VK filtering, but there does not appear to be a built-in global feature that rewrites/deduplicates `/v1/models` to expose only logical aliases while suppressing all raw provider-specific variants. For now, use routing + aliases + VK allowed_models for inference behavior, and add a thin proxy/filter in front of `/v1/models` if the client model picker must only see logical aliases.
