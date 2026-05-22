#!/usr/bin/env python3
"""Validate a planner JSON before showing the teacher-facing plan."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
DISPLAY_MAP_PATH = SKILL_ROOT / "references" / "exercise_type_display_map.json"
REFERENCES_ROOT = SKILL_ROOT / "references"

DOCUMENT_TYPES = {
    "worksheet",
    "revision_sheet",
    "quiz_15",
    "midterm_test",
    "end_of_unit_test",
    "final_exam",
    "custom_test",
}
GRADES = {6, 7, 8, 9}
NUMBERING = {"per_section", "global"}
OUTPUT_VERSIONS = {"student", "teacher_answer_key", "teacher_full"}
KNOWLEDGE_FOCUS_HINTS = {"vocabulary", "grammar", "reading", "listening", "writing", "speaking", "mixed"}
FORBIDDEN_EXERCISE_TYPES = {
    "Yes/No": "Use grammar_mcq/question_making for grammar focus, or reading_tf/listening_tf for comprehension.",
    "yes_no": "Use grammar_mcq/question_making for grammar focus, or reading_tf/listening_tf for comprehension.",
    "yes-no": "Use grammar_mcq/question_making for grammar focus, or reading_tf/listening_tf for comprehension.",
    "word_meaning_mcq": "Meaning translation MCQ is not allowed. Use vocab_mcq with English context.",
    "meaning_matching": "Meaning translation matching is not allowed. Use vocab_mcq with English context.",
    "meaning matching": "Meaning translation matching is not allowed. Use vocab_mcq with English context.",
    "true_false": "Use reading_tf or listening_tf.",
    "MCQ": "Use a specific type such as vocab_mcq, grammar_mcq, reading_mcq, or listening_mcq.",
    "TF": "Use reading_tf or listening_tf.",
    "fill_blank": "Use word_bank_gap_fill, grammar_gap_fill, reading_gap_fill, or listening_gap_fill.",
    "writing": "Use a specific writing type such as sentence_building or guided_paragraph.",
    "translation": "Translation is not in the approved format list.",
}
TECHNICAL_OUTPUT_PATTERNS = [
    "Producer Handoff",
    "Document type",
    "Document profile",
    "Document Blocks",
    "Cấu trúc bài tập",
    "Cấu trúc đề",
    "exercise_type",
    "knowledge_type",
    "block_type",
]
UNIT_SECTION_PATTERN = re.compile(r"^\s*unit\s+\d+\b", re.IGNORECASE)


def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}") from exc
    if not isinstance(data, dict):
        raise ValueError("Top-level JSON value must be an object.")
    return data


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
    except ValueError:
        return False
    return True


def validate_artifact_path(path: Path) -> list[str]:
    resolved = path.resolve()
    if is_relative_to(resolved, SKILL_ROOT) and not is_relative_to(resolved, REFERENCES_ROOT):
        return [
            "Generated plan files must not be stored under the skill directory. "
            "Write plan.json/blueprint.md under outputs/<slug>/ instead."
        ]
    return []


def load_display_map() -> dict[str, str]:
    with DISPLAY_MAP_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("exercise_type_display_map.json must be an object.")
    return {str(k): str(v) for k, v in data.items()}


def is_blank_text(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def contains_yes_no_format(text: str) -> bool:
    lowered = text.lower()
    if "grammar focus" in lowered or "trọng tâm" in lowered:
        return False
    return any(pattern in lowered for pattern in ["yes/no", "yes-no", "yes no"])


def looks_like_generic_reading_label(text: str) -> bool:
    normalized = re.sub(r"\s+", " ", text.lower()).strip()
    generic_labels = {
        "đọc và chọn đáp án",
        "đọc đoạn văn và chọn đáp án",
        "read and choose the best answer",
        "read and choose",
    }
    return normalized in generic_labels


def validate_required(data: dict[str, Any], errors: list[str]) -> None:
    required = [
        "document_type",
        "grade",
        "units",
        "title_header",
        "duration",
        "output_language",
        "numbering",
        "matrix_printed_in_docx",
        "output_versions",
        "sections",
        "content_sources",
        "special_requirements",
    ]
    for key in required:
        if key not in data:
            errors.append(f"Missing required field: {key}.")


def validate_top_level(data: dict[str, Any], errors: list[str]) -> None:
    if data.get("document_type") not in DOCUMENT_TYPES:
        errors.append(f"document_type must be one of: {', '.join(sorted(DOCUMENT_TYPES))}.")
    if data.get("grade") not in GRADES:
        errors.append("grade must be one of 6, 7, 8, 9.")
    if not isinstance(data.get("units"), list) or not data.get("units"):
        errors.append("units must be a non-empty list.")
    else:
        for idx, unit in enumerate(data["units"], start=1):
            if not isinstance(unit, dict) or not isinstance(unit.get("unit_number"), int):
                errors.append(f"units[{idx}] must contain integer unit_number.")
    for key in ["title_header", "duration", "output_language"]:
        if is_blank_text(data.get(key)):
            errors.append(f"{key} is required.")
    if data.get("numbering") not in NUMBERING:
        errors.append("numbering must be per_section or global.")
    if not isinstance(data.get("matrix_printed_in_docx"), bool):
        errors.append("matrix_printed_in_docx must be a boolean.")
    versions = data.get("output_versions")
    if not isinstance(versions, list) or not versions:
        errors.append("output_versions must be a non-empty list.")
    else:
        for version in versions:
            if version not in OUTPUT_VERSIONS:
                errors.append(f"Unsupported output version: {version}.")


def validate_sections(data: dict[str, Any], display_map: dict[str, str], errors: list[str]) -> None:
    sections = data.get("sections")
    if not isinstance(sections, list) or not sections:
        errors.append("sections must be a non-empty list.")
        return
    seen_sections: set[str] = set()
    for idx, section in enumerate(sections, start=1):
        if not isinstance(section, dict):
            errors.append(f"sections[{idx}] must be an object.")
            continue
        label = str(section.get("section") or idx)
        if label in seen_sections:
            errors.append(f"Duplicate section label: {label}.")
        seen_sections.add(label)
        for key in ["section", "focus", "exercise_type", "difficulty", "count", "layout_notes"]:
            if key not in section or is_blank_text(section.get(key)):
                errors.append(f"Section {label} missing required field: {key}.")
        exercise_type = section.get("exercise_type")
        if exercise_type in FORBIDDEN_EXERCISE_TYPES:
            errors.append(f"Section {label} uses forbidden exercise_type '{exercise_type}'. {FORBIDDEN_EXERCISE_TYPES[exercise_type]}")
            continue
        if exercise_type not in display_map:
            errors.append(f"Section {label} uses unsupported exercise_type '{exercise_type}'.")
            continue
        teacher_format = section.get("teacher_facing_format")
        expected = display_map[exercise_type]
        if teacher_format is not None and teacher_format != expected:
            errors.append(
                f"Section {label} teacher_facing_format must be exactly '{expected}' for exercise_type '{exercise_type}'."
            )
        try:
            difficulty = int(section.get("difficulty", 0) or 0)
        except (TypeError, ValueError):
            difficulty = 0
        if difficulty not in {1, 2, 3}:
            errors.append(f"Section {label} difficulty must be 1, 2, or 3.")
        if not isinstance(section.get("count"), int) or section.get("count", 0) <= 0:
            errors.append(f"Section {label} count must be a positive integer.")
        visible_text = " ".join(str(section.get(key) or "") for key in ["focus", "teacher_facing_format", "layout_notes"])
        if contains_yes_no_format(visible_text):
            errors.append(f"Section {label} uses Yes/No as visible exercise format. Keep it only as grammar focus if needed.")
        if looks_like_generic_reading_label(str(teacher_format or "")):
            errors.append(
                f"Section {label} uses a generic reading label. Use '{display_map['reading_mcq']}' or '{display_map['reading_gap_fill']}'."
            )
        if exercise_type == "reading_gap_fill" and re.search(r"\bword bank\b|word_bank|ngân hàng từ", visible_text, re.IGNORECASE):
            errors.append(f"Section {label} reading_gap_fill must not use a word bank; each blank has A/B/C/D options.")
        if exercise_type == "reading_mcq" and re.search(r"blank|gap|chỗ trống|ô trống|_{3,}", visible_text, re.IGNORECASE):
            errors.append(f"Section {label} reading_mcq looks like blank filling. Use reading_gap_fill.")
        if exercise_type == "stress_odd_one" and re.search(r"gạch chân|underline", visible_text, re.IGNORECASE):
            errors.append(f"Section {label} stress_odd_one must not require underlined parts.")
        if exercise_type == "pronunciation_odd_one" and not re.search(r"gạch chân|underline|cùng", visible_text, re.IGNORECASE):
            errors.append(f"Section {label} pronunciation_odd_one should mention underlined same letters/sounds.")


def validate_multi_unit_plan(data: dict[str, Any], errors: list[str]) -> None:
    units = data.get("units")
    if not isinstance(units, list) or len(units) <= 1:
        return
    for idx, section in enumerate(data.get("sections") or [], start=1):
        if not isinstance(section, dict):
            continue
        label_text = " ".join(str(section.get(key) or "") for key in ["section", "focus", "layout_notes"])
        if UNIT_SECTION_PATTERN.search(label_text):
            errors.append(
                f"Section {section.get('section') or idx} is organized by unit. "
                "For multi-unit requests, keep normal exercise sections and mix content from all units inside each exercise."
            )


def validate_content(data: dict[str, Any], errors: list[str]) -> None:
    content_sources = data.get("content_sources")
    if not isinstance(content_sources, dict):
        errors.append("content_sources must be an object.")
    special = data.get("special_requirements")
    if not isinstance(special, dict):
        errors.append("special_requirements must be an object.")
        return
    listening = bool(special.get("listening"))
    if listening and not special.get("transcript"):
        errors.append("special_requirements.transcript must be true when listening is true.")


def validate_markdown(text: str) -> list[str]:
    errors: list[str] = []
    for pattern in TECHNICAL_OUTPUT_PATTERNS:
        if pattern.lower() in text.lower():
            errors.append(f"Teacher-facing plan must not contain '{pattern}'.")
    if "| Thông tin |" in text:
        errors.append("Top information must be a list, not a table.")
    if text.strip().splitlines()[-1].strip().lower().startswith("### cấu trúc"):
        errors.append("Do not add a final structure section.")
    return errors


def validate(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    display_map = load_display_map()
    validate_required(data, errors)
    validate_top_level(data, errors)
    validate_sections(data, display_map, errors)
    validate_multi_unit_plan(data, errors)
    validate_content(data, errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Path to plan JSON, or Markdown when --markdown is set")
    parser.add_argument("--markdown", action="store_true", help="Validate teacher-facing Markdown for forbidden sections/labels")
    parser.add_argument("--json", action="store_true", help="Print machine-readable validation result")
    args = parser.parse_args()

    try:
        errors = validate_artifact_path(args.input)
        if args.markdown:
            errors.extend(validate_markdown(args.input.read_text(encoding="utf-8")))
        else:
            errors.extend(validate(load_json(args.input)))
    except Exception as exc:  # noqa: BLE001 - CLI should report concise validation failures.
        errors = [str(exc)]

    if args.json:
        print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    elif errors:
        print("Assessment plan is invalid:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
    else:
        print("Assessment plan is valid.")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
