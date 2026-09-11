#!/usr/bin/env python3
"""Query the endpoint used by Apple Developer Search.

The endpoint streams JSON Lines containing incremental diffs. This script
reassembles those diffs and prints one JSON document for an agent to consume.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from typing import Any


API_URL = "https://devintserv.msc.sbz.apple.com/api/v1/query"
DEFAULT_INCLUDED_RESPONSES = ["quickSearch", "search", "ask"]
FILTER_INCLUDED_RESPONSES = ["search"]
FILTER_CATEGORIES: dict[str, dict[str, Any]] = {
    "documentation": {"documentation": {}},
    "videos": {"videos": {}},
    "sample-code": {"sampleCode": {}},
    "wwdc26": {"wwdc": {"year": 2026}},
}
SUPPORTED_LOCALES = (
    "en",
    "de-DE",
    "fr-FR",
    "it-IT",
    "ja-JP",
    "ko-KR",
    "pt-BR",
    "zh-CN",
    "es-lamr",
)


class AskAppleError(RuntimeError):
    """Raised when Apple cannot return a usable response."""


def apply_diff(buffer: str, diff: dict[str, Any]) -> str:
    remove_last = diff.get("removeLast", 0)
    if isinstance(remove_last, int) and remove_last > 0:
        buffer = buffer[: max(0, len(buffer) - remove_last)]

    append = diff.get("append", "")
    if isinstance(append, str):
        buffer += append
    return buffer


def parse_buffer(buffer: str, channel: str) -> Any:
    if not buffer.strip():
        return None
    try:
        return json.loads(buffer)
    except json.JSONDecodeError as error:
        raise AskAppleError(
            f"Apple finished the {channel} stream with invalid JSON: {error}"
        ) from error


def query_apple(
    question: str,
    locale: str,
    timeout: float,
    filter_name: str | None = None,
) -> dict[str, Any]:
    included_responses = (
        FILTER_INCLUDED_RESPONSES if filter_name else DEFAULT_INCLUDED_RESPONSES
    )
    request_body: dict[str, Any] = {
        "text": question,
        "targetResultLocale": locale,
        "includedResponses": included_responses,
    }
    if filter_name:
        request_body["filterCategory"] = FILTER_CATEGORIES[filter_name]

    body = json.dumps(request_body).encode("utf-8")

    request = urllib.request.Request(
        API_URL,
        data=body,
        method="POST",
        headers={
            "Accept": "application/jsonl",
            "Content-Type": "application/json",
            "User-Agent": "Ask-Apple-Agent-Skill/1.0",
        },
    )

    buffers = {"ask": "", "search": ""}
    quick_search: Any = None
    finished = {"quickSearch": False, "search": False, "ask": False}
    endpoint_errors: list[Any] = []

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            content_type = response.headers.get_content_type()
            if content_type != "application/jsonl":
                raise AskAppleError(
                    f"Apple returned unexpected content type {content_type!r}"
                )

            for raw_line in response:
                line = raw_line.decode("utf-8").strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError as error:
                    raise AskAppleError(
                        f"Apple returned an invalid JSONL event: {error}"
                    ) from error

                kind = event.get("kind")
                if kind == "quickSearch":
                    quick_search = event.get("response")
                elif kind in buffers:
                    diff = event.get("diff")
                    if isinstance(diff, dict):
                        buffers[kind] = apply_diff(buffers[kind], diff)
                elif kind == "error":
                    endpoint_errors.append(event.get("response", event))
                elif isinstance(kind, str) and kind.endswith("Finished"):
                    channel = kind[: -len("Finished")]
                    if channel in finished:
                        finished[channel] = True

    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace").strip()
        suffix = f": {detail}" if detail else ""
        raise AskAppleError(f"Apple returned HTTP {error.code}{suffix}") from error
    except urllib.error.URLError as error:
        raise AskAppleError(f"Could not reach Apple Developer Search: {error.reason}") from error
    except TimeoutError as error:
        raise AskAppleError(f"Apple Developer Search timed out after {timeout:g}s") from error

    return {
        "query": question,
        "endpoint": API_URL,
        "targetResultLocale": locale,
        "includedResponses": included_responses,
        "filter": filter_name,
        "answer": parse_buffer(buffers["ask"], "ask"),
        "quickSearch": quick_search,
        "search": parse_buffer(buffers["search"], "search"),
        "finished": finished,
        "errors": endpoint_errors,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Ask Apple Developer Search and assemble its AI answer, quick results, "
            "and mixed search results, or run one focused category search."
        )
    )
    parser.add_argument("--question", required=True, help="Question to send to Apple")
    parser.add_argument(
        "--locale",
        choices=SUPPORTED_LOCALES,
        default="en",
        help="Target locale for Apple search results (default: en)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=120.0,
        help="Network timeout in seconds (default: 120)",
    )
    parser.add_argument(
        "--filter",
        choices=tuple(FILTER_CATEGORIES),
        help=(
            "Run a search-only request for one result category: documentation, "
            "videos, sample-code, or wwdc26"
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    question = args.question.strip()
    if not question:
        print("error: --question must not be empty", file=sys.stderr)
        return 2
    if args.timeout <= 0:
        print("error: --timeout must be greater than zero", file=sys.stderr)
        return 2

    try:
        result = query_apple(question, args.locale, args.timeout, args.filter)
    except AskAppleError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
