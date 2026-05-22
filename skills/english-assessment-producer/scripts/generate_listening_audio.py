#!/usr/bin/env python3
"""Generate listening MP3 files from an ElevenLabs audio manifest."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import requests


API_BASE = "https://api.elevenlabs.io/v1"
DEFAULT_OUTPUT_FORMAT = "mp3_44100_128"


def load_manifest(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("Audio manifest must be a JSON object.")
    items = data.get("items")
    if not isinstance(items, list) or not items:
        raise ValueError("Audio manifest must contain a non-empty items list.")
    return data


def safe_filename(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in ("-", "_", ".") else "-" for ch in value.strip())
    return cleaned or "audio.mp3"


def validate_item(item: dict[str, Any]) -> None:
    mode = item.get("mode", "single")
    if mode not in {"single", "dialogue"}:
        raise ValueError(f"Unsupported audio item mode: {mode}")
    if mode == "single":
        if not item.get("text"):
            raise ValueError(f"Single audio item {item.get('id')} is missing text.")
        if not item.get("voice_id"):
            raise ValueError(f"Single audio item {item.get('id')} is missing voice_id.")
    if mode == "dialogue":
        turns = item.get("turns")
        if not isinstance(turns, list) or not turns:
            raise ValueError(f"Dialogue audio item {item.get('id')} must contain turns.")
        for index, turn in enumerate(turns, start=1):
            if not isinstance(turn, dict) or not turn.get("text") or not turn.get("voice_id"):
                raise ValueError(f"Dialogue item {item.get('id')} turn {index} needs text and voice_id.")


def build_single_payload(item: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "text": item["text"],
        "model_id": item.get("model_id", "eleven_multilingual_v2"),
    }
    for optional_key in [
        "language_code",
        "voice_settings",
        "pronunciation_dictionary_locators",
        "seed",
        "previous_text",
        "next_text",
        "apply_text_normalization",
    ]:
        if item.get(optional_key) is not None:
            payload[optional_key] = item[optional_key]
    return payload


def build_dialogue_payload(item: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "inputs": [{"text": turn["text"], "voice_id": turn["voice_id"]} for turn in item["turns"]],
        "model_id": item.get("model_id", "eleven_v3"),
    }
    for optional_key in [
        "language_code",
        "settings",
        "pronunciation_dictionary_locators",
        "seed",
        "apply_text_normalization",
    ]:
        if item.get(optional_key) is not None:
            payload[optional_key] = item[optional_key]
    return payload


def call_elevenlabs(item: dict[str, Any], api_key: str, timeout: int, output_format: str) -> bytes:
    mode = item.get("mode", "single")
    headers = {"xi-api-key": api_key, "Content-Type": "application/json"}
    params = {"output_format": item.get("output_format", output_format)}

    if mode == "single":
        url = f"{API_BASE}/text-to-speech/{item['voice_id']}"
        payload = build_single_payload(item)
    else:
        url = f"{API_BASE}/text-to-dialogue"
        payload = build_dialogue_payload(item)

    response = requests.post(url, headers=headers, params=params, json=payload, timeout=timeout)
    if response.status_code >= 400:
        raise RuntimeError(f"ElevenLabs returned {response.status_code}: {response.text[:500]}")
    return response.content


def output_file_for(item: dict[str, Any]) -> str:
    if item.get("output_file"):
        return safe_filename(str(item["output_file"]))
    item_id = safe_filename(str(item.get("id") or "listening"))
    return item_id if item_id.endswith(".mp3") else f"{item_id}.mp3"


def generate(manifest_path: Path, out_dir: Path, dry_run: bool, timeout: int, output_format: str) -> list[dict[str, str]]:
    manifest = load_manifest(manifest_path)
    items = [item for item in manifest["items"] if isinstance(item, dict)]
    if len(items) != len(manifest["items"]):
        raise ValueError("Every item in audio manifest must be an object.")

    for item in items:
        validate_item(item)

    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key and not dry_run:
        raise EnvironmentError(
            "ELEVENLABS_API_KEY is not set. Set it to generate MP3 files, or use --dry-run to validate only."
        )

    out_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, str]] = []
    for item in items:
        output_path = out_dir / output_file_for(item)
        if dry_run:
            results.append({"id": str(item.get("id", "")), "status": "validated", "output": str(output_path)})
            continue
        audio = call_elevenlabs(item, api_key=api_key or "", timeout=timeout, output_format=output_format)
        output_path.write_bytes(audio)
        results.append({"id": str(item.get("id", "")), "status": "generated", "output": str(output_path)})
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path, help="Path to audio manifest JSON")
    parser.add_argument("--out-dir", required=True, type=Path, help="Directory for generated MP3 files")
    parser.add_argument("--dry-run", action="store_true", help="Validate manifest without calling ElevenLabs")
    parser.add_argument("--timeout", type=int, default=120, help="HTTP timeout in seconds")
    parser.add_argument("--output-format", default=DEFAULT_OUTPUT_FORMAT, help="ElevenLabs output_format query value")
    args = parser.parse_args()

    try:
        results = generate(args.manifest, args.out_dir, args.dry_run, args.timeout, args.output_format)
    except Exception as exc:  # noqa: BLE001 - CLI should report concise generation failures.
        print(f"Audio generation failed: {exc}", file=sys.stderr)
        return 1

    print(json.dumps({"results": results}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
