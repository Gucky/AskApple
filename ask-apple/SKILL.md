---
name: ask-apple
description: Ask Apple Developer questions through Apple's AI-backed online search and return the generated answer, quick results, mixed search results, and optional category-specific results with Apple source links. Use when a user explicitly asks to use Ask Apple or wants Apple Developer's own online answer to a development question.
---

# Ask Apple

Send the user's question to [Apple Developer Search](https://developer.apple.com/search/). By default, retrieve all three response channels in one request:

- `quickSearch` for quick results.
- `search` for the mixed results shown under **All**.
- `ask` for Apple's AI-generated answer and its sources.

## Request

Send only the question the user wants Apple to answer. Do not add repository contents, local files, hidden context, credentials, or personal data. Preserve the user's wording unless they ask for the question to be rewritten.

Run the bundled script with an absolute path resolved relative to this `SKILL.md`:

```bash
python3 <skill-directory>/scripts/ask_apple.py --question '<question>' --locale en
```

Choose the closest supported result locale when it helps the search results: `en`, `de-DE`, `fr-FR`, `it-IT`, `ja-JP`, `ko-KR`, `pt-BR`, `zh-CN`, or `es-lamr`. The endpoint may still generate the AI answer in English. Do not ask the user to choose among the three response channels; the script always requests all of them.

The script emits one assembled JSON document rather than Apple's streamed diffs. It contains `answer`, `quickSearch`, `search`, the active `filter`, completion flags, and any endpoint-reported errors.

## Category Search

The **All** results are a ranked mixture, not an exhaustive union of the category tabs. Do not request every category by default.

When the user asks to search specifically for Documentation, Videos, Sample Code, or WWDC26 material, run a separate filtered request for each requested category:

```bash
python3 <skill-directory>/scripts/ask_apple.py --question '<question>' --locale en --filter documentation
python3 <skill-directory>/scripts/ask_apple.py --question '<question>' --locale en --filter videos
python3 <skill-directory>/scripts/ask_apple.py --question '<question>' --locale en --filter sample-code
python3 <skill-directory>/scripts/ask_apple.py --question '<question>' --locale en --filter wwdc26
```

A filtered request retrieves only the `search` channel for that category. If the user names multiple categories, run only those requested filters; they may run concurrently. Preserve the original question unless the user asks to change it.

## Response

Lead with Apple's AI-generated answer and label it clearly as such. Then provide:

1. Quick results, if present.
2. Mixed **All** search results, grouped compactly into useful result types when helpful.
3. Direct Apple links for cited sources and results.

For a category-specific follow-up, label the requested category and present its search results without repeating the earlier AI answer unless the user asks for it.

Keep Apple's answer distinct from your own interpretation. Mention that Apple labels generated answers as AI-generated and recommends verifying them. If the user asks for analysis, you may evaluate the returned material after presenting what Apple returned.

## Failure Handling

If Apple returns an HTTP error, times out, or changes the response schema, report that clearly. Do not fabricate missing channels or silently substitute a different search provider.
