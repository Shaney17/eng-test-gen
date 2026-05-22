#!/usr/bin/env python3
"""Validate an English assessment JSON source file."""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
REFERENCES_ROOT = SKILL_ROOT / "references"

QUESTION_TYPES_WITH_OPTIONS = {
    "pronunciation_odd_one",
    "stress_odd_one",
    "vocab_mcq",
    "grammar_mcq",
    "dialogue_completion",
    "reading_mcq",
    "reading_gap_fill",
    "reference_word",
    "closest_opposite_meaning",
    "notice_reading",
    "sentence_insertion",
    "listening_mcq",
    "listening_tf",
    "matching",
}
SUPPORTED_EXERCISE_TYPES = {
    "pronunciation_odd_one",
    "stress_odd_one",
    "vocab_mcq",
    "matching",
    "word_bank_gap_fill",
    "missing_letters",
    "word_form",
    "odd_one_topic",
    "label_picture",
    "crossword",
    "grammar_mcq",
    "verb_form",
    "grammar_gap_fill",
    "choose_between_forms",
    "error_correction",
    "sentence_rewrite",
    "rewrite_with_given_word",
    "sentence_combining",
    "sentence_building",
    "question_making",
    "dialogue_completion",
    "dialogue_ordering",
    "speaking_card",
    "reading_mcq",
    "reading_tf",
    "reading_gap_fill",
    "short_answer",
    "heading_matching",
    "reference_word",
    "closest_opposite_meaning",
    "notice_reading",
    "sentence_ordering",
    "sentence_insertion",
    "listening_mcq",
    "listening_tf",
    "listening_gap_fill",
    "listening_table_completion",
    "listening_matching",
    "guided_sentence_writing",
    "guided_paragraph",
    "email_writing",
    "picture_prompt_writing",
    "word_form_writing",
}
FORBIDDEN_EXERCISE_TYPES = {
    "Yes/No": "Use reading_tf, listening_tf, or short_answer.",
    "yes_no": "Use reading_tf, listening_tf, or short_answer.",
    "yes-no": "Use reading_tf, listening_tf, or short_answer.",
    "word_meaning_mcq": "Meaning translation MCQ is not allowed. Use English-context vocab_mcq.",
    "meaning_matching": "Meaning translation matching is not allowed. Use English-context vocab_mcq.",
    "meaning matching": "Meaning translation matching is not allowed. Use English-context vocab_mcq.",
    "true_false": "Use reading_tf or listening_tf.",
    "MCQ": "Use a specific type such as vocab_mcq, grammar_mcq, reading_mcq, or listening_mcq.",
    "TF": "Use reading_tf or listening_tf.",
    "fill_blank": "Use word_bank_gap_fill, grammar_gap_fill, reading_gap_fill, or listening_gap_fill.",
    "ordering": "Use sentence_ordering or dialogue_ordering.",
    "writing": "Use sentence_building, sentence_rewrite, guided_sentence_writing, guided_paragraph, or email_writing.",
    "translation": "Translation is not in the approved format list.",
}
SUPPORTED_BLOCK_TYPES = {
    "heading",
    "text",
    "vocabulary_table",
    "resource_table",
    "word_bank",
    "crossword",
    "notice_box",
    "passage",
    "question_group",
}
SUPPORTED_NUMBERING = {"global", "per_section"}
WORKSHEET_DOCUMENT_TYPES = {"worksheet", "revision_sheet", "practice_sheet", "homework", "topic_practice"}
EXAM_DOCUMENT_TYPE_HINTS = ("test", "exam", "quiz", "midterm", "final", "end_term", "end-of-unit")
LEADING_QUESTION_LABEL_PATTERN = re.compile(
    r"^\s*(?:question|câu)\s*\d+\s*[\.:)]\s*|^\s*[A-Za-z]?\d+\s*[\.:)]\s*",
    re.IGNORECASE,
)
UNDERLINE_PATTERN = re.compile(r"__([^_\s](?:.*?[^_\s])?)__")
SPEAKER_LABEL_PATTERN = re.compile(r"(?<!\w)([A-ZÀ-Ỹ][A-Za-zÀ-ỹ' -]{0,24}):")
UNIT_HEADING_PATTERN = re.compile(r"^\s*unit\s+\d+\b", re.IGNORECASE)
ENGLISH_WORD_PATTERN = re.compile(r"^[A-Za-z][A-Za-z'-]*$")


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
            "Generated assessment files must not be stored under the skill directory. "
            "Write assessment.json under outputs/<slug>/ instead."
        ]
    return []


def default_kb_db_path() -> Path | None:
    env_path = os.environ.get("ENGLISH_KB_DB_PATH")
    candidates = []
    if env_path:
        candidates.append(Path(env_path))
    candidates.extend(
        [
            Path.cwd() / "knowledge_base.db",
            SKILL_ROOT.parents[1] / "knowledge_base.db" if len(SKILL_ROOT.parents) > 1 else SKILL_ROOT / "knowledge_base.db",
        ]
    )
    for candidate in candidates:
        if candidate and candidate.exists():
            return candidate
    return None


def normalize_vocab_word(value: str) -> str:
    text = UNDERLINE_PATTERN.sub(r"\1", str(value or ""))
    text = re.sub(r"^\s*[A-D]\s*[\.:)]\s*", "", text, flags=re.IGNORECASE)
    text = text.strip().lower()
    text = re.sub(r"^\(to\)\s+", "", text)
    return text


def vocab_tokens(value: str) -> set[str]:
    normalized = normalize_vocab_word(value)
    tokens = {normalized} if ENGLISH_WORD_PATTERN.fullmatch(normalized) else set()
    for token in re.findall(r"[A-Za-z][A-Za-z'-]*", normalized):
        if len(token) > 1:
            tokens.add(token.lower())
    return tokens


def load_kb_vocab_words(db_path: Path | None) -> set[str] | None:
    if not db_path:
        return None
    try:
        with sqlite3.connect(str(db_path)) as conn:
            rows = conn.execute("select word from vocabulary").fetchall()
    except sqlite3.Error:
        return None
    words: set[str] = set()
    for (word,) in rows:
        words.update(vocab_tokens(str(word or "")))
    return words


def as_number(value: Any, default: float = 0.0) -> float:
    if value is None or isinstance(value, bool):
        return default
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return default


def get_answer_key(data: dict[str, Any]) -> dict[str, Any]:
    raw = data.get("answer_key", [])
    if isinstance(raw, dict):
        return {str(k): v for k, v in raw.items()}
    answers: dict[str, Any] = {}
    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, dict) and item.get("question_id"):
                answers[str(item["question_id"])] = item.get("answer")
    return answers


def question_sort_key(question_id: str) -> tuple[str, int]:
    match = re.fullmatch(r"([A-Za-z_ -]*?)(\d+)", question_id.strip())
    if not match:
        return question_id, -1
    return match.group(1), int(match.group(2))


def iter_section_questions(data: dict[str, Any]):
    for section_index, section in enumerate(data.get("sections") or [], start=1):
        if not isinstance(section, dict):
            continue
        section_id = str(section.get("id") or section_index)
        for question_index, question in enumerate(section.get("questions") or [], start=1):
            if isinstance(question, dict):
                yield {
                    "container_type": "section",
                    "container_id": section_id,
                    "container": section,
                    "question_index": question_index,
                    "question": question,
                }


def iter_block_questions(data: dict[str, Any]):
    for block_index, block in enumerate(data.get("blocks") or [], start=1):
        if not isinstance(block, dict):
            continue
        block_type = block.get("type")
        if block_type != "question_group":
            continue
        block_id = str(block.get("id") or block_index)
        for question_index, question in enumerate(block.get("questions") or [], start=1):
            if isinstance(question, dict):
                yield {
                    "container_type": "block",
                    "container_id": block_id,
                    "container": block,
                    "question_index": question_index,
                    "question": question,
                }


def iter_questions(data: dict[str, Any]):
    yielded = False
    for item in iter_block_questions(data):
        yielded = True
        yield item
    if not yielded:
        yield from iter_section_questions(data)


def iter_question_groups_with_neighbors(data: dict[str, Any]):
    blocks = data.get("blocks")
    if not isinstance(blocks, list):
        return
    for index, block in enumerate(blocks):
        if isinstance(block, dict) and block.get("type") == "question_group":
            previous_block = blocks[index - 1] if index > 0 and isinstance(blocks[index - 1], dict) else None
            next_block = blocks[index + 1] if index + 1 < len(blocks) and isinstance(blocks[index + 1], dict) else None
            yield index + 1, block, previous_block, next_block


def question_id_for(item: dict[str, Any]) -> str:
    question = item["question"]
    return str(question.get("id") or "").strip()


def validate_metadata(data: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    metadata = data.get("metadata")
    if not isinstance(metadata, dict):
        errors.append("metadata must be an object.")
        return {}

    if not metadata.get("title"):
        errors.append("metadata.title is required.")
    if metadata.get("grade") is not None and metadata.get("grade") not in [6, 7, 8, 9]:
        errors.append("metadata.grade must be one of 6, 7, 8, 9.")
    profile = metadata.get("document_profile")
    if profile is not None and profile not in {"worksheet", "exam"}:
        errors.append("metadata.document_profile must be worksheet or exam when present.")
    return metadata


def is_exam_like(metadata: dict[str, Any]) -> bool:
    profile = str(metadata.get("document_profile") or "").strip().lower()
    if profile == "exam":
        return True
    if profile == "worksheet":
        return False
    document_type = str(metadata.get("document_type") or "").strip().lower()
    if document_type in WORKSHEET_DOCUMENT_TYPES:
        return False
    return any(hint in document_type for hint in EXAM_DOCUMENT_TYPE_HINTS)


def validate_rendering(data: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    rendering = data.get("rendering") or {}
    if not isinstance(rendering, dict):
        errors.append("rendering must be an object when present.")
        return {}
    numbering = rendering.get("question_numbering")
    if numbering is not None and numbering not in SUPPORTED_NUMBERING:
        errors.append("rendering.question_numbering must be global or per_section.")
    return rendering


def validate_blocks(data: dict[str, Any], errors: list[str]) -> None:
    blocks = data.get("blocks")
    sections = data.get("sections")
    if blocks is None and sections is None:
        errors.append("Either blocks or sections must be present.")
        return
    if blocks is not None and (not isinstance(blocks, list) or not blocks):
        errors.append("blocks must be a non-empty list when present.")
        return

    if not isinstance(blocks, list):
        return

    previous_block_type = ""
    next_block_type = ""
    for index, block in enumerate(blocks, start=1):
        if not isinstance(block, dict):
            errors.append(f"blocks[{index}] must be an object.")
            continue
        block_type = block.get("type")
        if block_type not in SUPPORTED_BLOCK_TYPES:
            errors.append(f"Block {block.get('id') or index} has unsupported type: {block_type}.")
            continue
        next_block = blocks[index] if index < len(blocks) and isinstance(blocks[index], dict) else {}
        next_block_type = str(next_block.get("type") or "")
        next_exercise_type = str(next_block.get("exercise_type") or "")

        if block_type in {"vocabulary_table", "resource_table"}:
            rows = block.get("rows")
            columns = block.get("columns")
            if not isinstance(columns, list) or not columns:
                errors.append(f"Block {block.get('id') or index} needs non-empty columns.")
            if not isinstance(rows, list) or not rows:
                errors.append(f"Block {block.get('id') or index} needs non-empty rows.")
        elif block_type == "word_bank":
            words = block.get("words") or block.get("items")
            if not isinstance(words, list) or not words:
                errors.append(f"Word bank block {block.get('id') or index} needs words/items.")
            if next_block_type != "question_group" or next_exercise_type != "word_bank_gap_fill":
                errors.append(
                    f"Word bank block {block.get('id') or index} must be placed immediately before a word_bank_gap_fill question_group."
                )
        elif block_type == "crossword":
            grid = block.get("grid")
            if not isinstance(grid, list) or not grid or not all(isinstance(row, list) for row in grid):
                errors.append(f"Crossword block {block.get('id') or index} needs a 2D grid.")
        elif block_type in {"notice_box", "passage", "text"} and not block.get("text"):
            errors.append(f"Block {block.get('id') or index} needs text.")
        elif block_type == "question_group":
            questions = block.get("questions")
            if not isinstance(questions, list) or not questions:
                errors.append(f"Question group {block.get('id') or index} needs non-empty questions.")
            validate_exercise_type(block.get("exercise_type"), f"Block {block.get('id') or index}", errors)
            if block.get("exercise_type") == "reading_gap_fill" and previous_block_type == "word_bank":
                errors.append(
                    f"Question group {block.get('id') or index} uses reading_gap_fill but has a word_bank immediately before it. "
                    "Cloze reading uses MCQ options per blank, not a separate word bank."
                )
            if block.get("exercise_type") == "reading_gap_fill" and (block.get("word_bank") or block.get("words")):
                errors.append(
                    f"Question group {block.get('id') or index} uses reading_gap_fill but includes a word bank. "
                    "Use options on each blank instead."
                )
            if block.get("exercise_type") == "word_bank_gap_fill" and previous_block_type != "word_bank":
                errors.append(
                    f"Question group {block.get('id') or index} uses word_bank_gap_fill but does not have a word_bank block immediately before it."
                )
        previous_block_type = str(block_type or "")


def validate_sections(data: dict[str, Any], errors: list[str]) -> None:
    sections = data.get("sections")
    if sections is None:
        return
    if not isinstance(sections, list) or not sections:
        errors.append("sections must be a non-empty list when present.")
        return
    for section_index, section in enumerate(sections, start=1):
        if not isinstance(section, dict):
            errors.append(f"sections[{section_index}] must be an object.")
            continue
        questions = section.get("questions")
        if not isinstance(questions, list) or not questions:
            errors.append(f"Section {section.get('id') or section_index} must contain a non-empty questions list.")
        validate_exercise_type(section.get("exercise_type"), f"Section {section.get('id') or section_index}", errors)


def validate_exercise_type(value: Any, location: str, errors: list[str]) -> None:
    if value is None:
        return
    if not isinstance(value, str):
        errors.append(f"{location} exercise_type must be a string.")
        return
    if value in FORBIDDEN_EXERCISE_TYPES:
        errors.append(f"{location} uses forbidden exercise_type '{value}'. {FORBIDDEN_EXERCISE_TYPES[value]}")
        return
    if value not in SUPPORTED_EXERCISE_TYPES:
        errors.append(f"{location} uses unsupported exercise_type '{value}'. Use the closed allowlist in exercise_formats.md.")


def looks_like_translation_meaning_prompt(text: str) -> bool:
    lowered = text.lower()
    if "notice" in lowered or "sign" in lowered or "announcement" in lowered:
        return False
    patterns = [
        "which word means",
        "what does “",
        "what does \"",
        "what does '",
        "mean?",
        "means \"",
        "means '",
        "có nghĩa là",
        "nghĩa là",
        "từ nào có nghĩa",
    ]
    return any(pattern in lowered for pattern in patterns)


def looks_like_yes_no_format_label(text: str) -> bool:
    lowered = text.lower()
    if "grammar focus" in lowered or "content focus" in lowered:
        return False
    patterns = ["yes/no", "yes-no", "yes no"]
    return any(pattern in lowered for pattern in patterns)


def has_leading_question_label(text: str) -> bool:
    return bool(LEADING_QUESTION_LABEL_PATTERN.search(text or ""))


def has_underline_markup(value: Any) -> bool:
    if isinstance(value, str):
        return bool(UNDERLINE_PATTERN.search(value))
    if isinstance(value, dict):
        return any(has_underline_markup(v) for v in value.values())
    if isinstance(value, list):
        return any(has_underline_markup(item) for item in value)
    return False


def normalize_answer(value: Any) -> str:
    if isinstance(value, dict):
        value = value.get("answer") or value.get("value")
    return str(value or "").strip().lower()


def is_valid_tf_ng_answer(value: Any) -> bool:
    normalized = normalize_answer(value)
    return normalized in {"t", "f", "ng", "true", "false", "not given"}


def has_rewrite_cue_word(question: dict[str, Any]) -> bool:
    if question.get("given_word") or question.get("cue_word"):
        return True
    stem = str(question.get("stem") or question.get("prompt") or "")
    return bool(re.search(r"\([A-Za-z][A-Za-z -]{1,30}\)", stem))


def has_rewrite_response_prompt(question: dict[str, Any]) -> bool:
    return bool(question.get("prompt") or question.get("answer_start") or question.get("rewrite_start") or question.get("response_start"))


def option_texts_have_embedded_labels(options: Any) -> bool:
    if not isinstance(options, list):
        return False
    for idx, option in enumerate(options):
        label = chr(ord("A") + idx)
        text = option.get("text") if isinstance(option, dict) else option
        if isinstance(text, str) and re.match(rf"^\s*{label}\s*[\.:)]\s+", text, flags=re.IGNORECASE):
            return True
    return False


def normalized_option_text(option: Any, index: int) -> str:
    label = chr(ord("A") + index)
    text = option.get("text") if isinstance(option, dict) else option
    text = str(text or "")
    text = UNDERLINE_PATTERN.sub(r"\1", text)
    return re.sub(rf"^\s*{label}\s*[\.:)]\s*", "", text, flags=re.IGNORECASE).strip()


def option_texts_have_phrases(options: Any) -> bool:
    if not isinstance(options, list):
        return False
    for idx, option in enumerate(options):
        text = normalized_option_text(option, idx)
        if re.search(r"\s", text):
            return True
    return False


def phonetics_option_words(options: Any) -> list[str]:
    if not isinstance(options, list):
        return []
    words = []
    for idx, option in enumerate(options):
        words.append(normalize_vocab_word(normalized_option_text(option, idx)))
    return words


def allowed_phonetics_words(data: dict[str, Any]) -> set[str]:
    metadata = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}
    raw_words = metadata.get("allowed_phonetics_words") or metadata.get("allowed_external_phonetics_words") or []
    if not isinstance(raw_words, list):
        return set()
    allowed: set[str] = set()
    for word in raw_words:
        allowed.update(vocab_tokens(str(word or "")))
    return allowed


def validate_phonetics_vocab(
    data: dict[str, Any],
    kb_vocab_words: set[str] | None,
    errors: list[str],
) -> None:
    if kb_vocab_words is None:
        return
    allowed_words = allowed_phonetics_words(data)
    for item in iter_questions(data):
        container = item["container"]
        question = item["question"]
        q_type = question.get("exercise_type", container.get("exercise_type"))
        if q_type not in {"pronunciation_odd_one", "stress_odd_one"}:
            continue
        question_id = question_id_for(item) or f"{item['container_id']}.{item['question_index']}"
        for word in phonetics_option_words(question.get("options")):
            if not word:
                continue
            if not ENGLISH_WORD_PATTERN.fullmatch(word):
                errors.append(
                    f"Question {question_id} phonetics option '{word}' is not a plain English word. "
                    "Use only alphabetic English words from the KB."
                )
                continue
            if word not in kb_vocab_words and word not in allowed_words:
                errors.append(
                    f"Question {question_id} phonetics option '{word}' is not found in knowledge_base.db. "
                    "Use KB vocabulary, or add a teacher-approved exception in metadata.allowed_phonetics_words."
                )


def pronunciation_underline_values(options: Any) -> list[str]:
    if not isinstance(options, list):
        return []
    values: list[str] = []
    for option in options:
        text = option.get("text") if isinstance(option, dict) else option
        matches = UNDERLINE_PATTERN.findall(str(text or ""))
        if not matches:
            values.append("")
        else:
            values.append(matches[0].strip().lower())
    return values


def pronunciation_underlines_are_consistent(options: Any) -> bool:
    values = pronunciation_underline_values(options)
    return bool(values) and all(values) and len(set(values)) == 1


def looks_like_blank_filling(text: str) -> bool:
    return bool(re.search(r"_{3,}|\(\s*\d+\s*\)\s*_{2,}|\bblank\b|\bgap\b", text or "", re.IGNORECASE))


def looks_like_question(text: str) -> bool:
    stripped = (text or "").strip()
    return stripped.endswith("?") or bool(
        re.match(r"^(what|where|when|why|who|whose|which|how|does|do|did|is|are|was|were|can|could|should)\b", stripped, re.IGNORECASE)
    )


def is_listening_type(exercise_type: Any) -> bool:
    return isinstance(exercise_type, str) and exercise_type.startswith("listening_")


def speaker_labels_in_line(line: str) -> list[str]:
    return SPEAKER_LABEL_PATTERN.findall(line or "")


def transcript_has_wrapped_dialogue(transcript: str) -> bool:
    for line in str(transcript or "").splitlines():
        if len(speaker_labels_in_line(line)) > 1:
            return True
    return False


def looks_like_dialogue_transcript(text: str) -> bool:
    labels = SPEAKER_LABEL_PATTERN.findall(text or "")
    return len(labels) >= 2


def validate_multi_unit_structure(data: dict[str, Any], errors: list[str]) -> None:
    metadata = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}
    units = metadata.get("units")
    if not isinstance(units, list) or len(units) <= 1:
        return

    for index, block in enumerate(data.get("blocks") or [], start=1):
        if not isinstance(block, dict) or block.get("type") != "question_group":
            continue
        visible_label = " ".join(str(block.get(key) or "") for key in ["id", "title", "instructions"])
        if UNIT_HEADING_PATTERN.search(visible_label):
            errors.append(
                f"Block {block.get('id') or index} is organized as a separate unit exercise. "
                "For multi-unit requests, keep normal exercise types and mix content from all requested units inside each exercise."
            )


def validate_listening_transcript(data: dict[str, Any], errors: list[str]) -> None:
    listening_question_groups = []
    for index, block, previous_block, _next_block in iter_question_groups_with_neighbors(data) or []:
        if not is_listening_type(block.get("exercise_type")):
            continue
        listening_question_groups.append(block)
        block_label = block.get("id") or index
        if block.get("passage") or block.get("transcript"):
            errors.append(
                f"Listening question group {block_label} must not print transcript/passage in the student question area. "
                "Put the full script only in top-level listening.transcript."
            )
        if previous_block and previous_block.get("type") == "passage":
            errors.append(
                f"Listening question group {block_label} has a passage block immediately before it. "
                "Do not place the listening transcript in the student copy."
            )
        for question_index, question in enumerate(block.get("questions") or [], start=1):
            if isinstance(question, dict) and question.get("passage"):
                errors.append(
                    f"Listening question {question.get('id') or str(block_label) + '.' + str(question_index)} must not contain passage/transcript text."
                )

    has_listening_questions = bool(listening_question_groups) or any(
        is_listening_type((item["question"].get("exercise_type") or item["container"].get("exercise_type")))
        for item in iter_questions(data)
    )
    listening = data.get("listening")
    if has_listening_questions:
        if not isinstance(listening, dict) or not listening.get("transcript"):
            errors.append("Listening exercises require top-level listening.transcript for the answer key section.")
        elif transcript_has_wrapped_dialogue(str(listening.get("transcript") or "")):
            errors.append(
                "listening.transcript dialogue must put each speaker turn on a separate line, e.g. 'Mai: ...\\nNam: ...'."
            )

    if isinstance(listening, dict) and listening.get("transcript"):
        transcript = str(listening.get("transcript") or "")
        if looks_like_dialogue_transcript(transcript) and transcript_has_wrapped_dialogue(transcript):
            errors.append("Dialogue transcript is not line-broken by speaker turn.")


def validate_matrix(data: dict[str, Any], errors: list[str], total_questions: int) -> None:
    matrix = data.get("matrix", [])
    if matrix is not None and not isinstance(matrix, list):
        errors.append("matrix must be a list when present.")
        return

    matrix_total = sum(int(as_number(row.get("count"), 0)) for row in matrix if isinstance(row, dict))
    if matrix_total and matrix_total != total_questions:
        errors.append(f"Total questions ({total_questions}) do not match matrix total ({matrix_total}).")

    matrix_by_id = {}
    for row in matrix:
        if not isinstance(row, dict):
            errors.append("Each matrix row must be an object.")
            continue
        validate_exercise_type(row.get("exercise_type"), f"Matrix row {row.get('title') or row.get('section_id') or row.get('block_id')}", errors)
        row_id = str(row.get("section_id") or row.get("block_id") or "").strip()
        if row_id:
            matrix_by_id[row_id] = row

    if not matrix_by_id:
        return

    counts_by_container: dict[str, int] = {}
    for item in iter_questions(data):
        cid = str(item["container_id"])
        counts_by_container[cid] = counts_by_container.get(cid, 0) + 1

    for container_id, row in matrix_by_id.items():
        expected = int(as_number(row.get("count"), -1))
        actual = counts_by_container.get(container_id)
        if actual is not None and expected != actual:
            errors.append(f"Container {container_id} question count is {actual} but matrix expects {expected}.")


def validate_questions(data: dict[str, Any], errors: list[str]) -> tuple[int, float]:
    answer_key = get_answer_key(data)
    seen_question_ids: set[str] = set()
    total_questions = 0
    calculated_points = 0.0

    for item in iter_questions(data):
        container = item["container"]
        question = item["question"]
        container_id = item["container_id"]
        question_index = item["question_index"]
        total_questions += 1

        question_id = question_id_for(item)
        if not question_id:
            errors.append(f"Question {container_id}.{question_index} is missing id.")
        elif question_id in seen_question_ids:
            errors.append(f"Duplicate question id: {question_id}.")
        else:
            seen_question_ids.add(question_id)

        q_type = question.get("exercise_type", container.get("exercise_type"))
        if (
            not question.get("stem")
            and not question.get("prompt")
            and not question.get("passage")
            and not (q_type in {"pronunciation_odd_one", "stress_odd_one", "odd_one_topic"} and question.get("options"))
        ):
            errors.append(f"Question {question_id or container_id + '.' + str(question_index)} needs stem, prompt, or passage.")

        validate_exercise_type(q_type, f"Question {question_id or container_id + '.' + str(question_index)}", errors)
        container_label_text = " ".join(
            str(container.get(key) or "") for key in ["title", "instructions", "exercise_format"]
        )
        if looks_like_yes_no_format_label(container_label_text):
            errors.append(
                f"Container {container_id} uses 'Yes/No' as a visible format label. "
                "Use grammar_mcq/question_making as the format; keep 'Yes/No questions' only in grammar focus."
            )
        stem_text = " ".join(s for s in [str(question.get("stem") or ""), str(question.get("prompt") or "")] if s)
        if has_leading_question_label(stem_text):
            errors.append(
                f"Question {question_id or container_id + '.' + str(question_index)} includes a leading question number in its stem. "
                "Keep numbering in display_label/renderer only."
            )
        if q_type == "vocab_mcq" and looks_like_translation_meaning_prompt(stem_text):
            errors.append(
                f"Question {question_id or container_id + '.' + str(question_index)} looks like meaning translation. "
                "Use an English context sentence for vocab_mcq."
            )
        if q_type == "reading_tf":
            if question.get("options") or question.get("items"):
                errors.append(
                    f"Question {question_id or container_id + '.' + str(question_index)} uses reading_tf but includes options/items. "
                    "Students must write T/F/NG in a blank, not choose A/B/C."
                )
            answer_value = question.get("answer", answer_key.get(question_id))
            if answer_value is not None and not is_valid_tf_ng_answer(answer_value):
                errors.append(
                    f"Question {question_id or container_id + '.' + str(question_index)} reading_tf answer must be T, F, or NG."
                )
        if q_type == "reading_mcq" and looks_like_blank_filling(stem_text):
            errors.append(
                f"Question {question_id or container_id + '.' + str(question_index)} uses reading_mcq but looks like a blank-filling item. Use reading_gap_fill."
            )
        if q_type == "reading_gap_fill":
            passage_text = str(container.get("passage") or container.get("text") or "")
            if not looks_like_blank_filling(stem_text) and not looks_like_blank_filling(passage_text):
                errors.append(
                    f"Question {question_id or container_id + '.' + str(question_index)} uses reading_gap_fill but has no numbered blank/gap in the stem or passage."
                )
            if looks_like_question(stem_text) and not looks_like_blank_filling(stem_text):
                errors.append(
                    f"Question {question_id or container_id + '.' + str(question_index)} uses reading_gap_fill but looks like a comprehension question. Use reading_mcq."
                )
        if q_type == "rewrite_with_given_word" and not has_rewrite_cue_word(question):
            errors.append(
                f"Question {question_id or container_id + '.' + str(question_index)} uses rewrite_with_given_word but has no given_word/cue_word."
            )
        if q_type in {"sentence_rewrite", "rewrite_with_given_word"} and not has_rewrite_response_prompt(question):
            errors.append(
                f"Question {question_id or container_id + '.' + str(question_index)} uses {q_type} but has no answer prompt/start for students."
            )
        if q_type == "question_making" and not has_underline_markup(stem_text):
            errors.append(
                f"Question {question_id or container_id + '.' + str(question_index)} uses question_making but has no __underlined part__."
            )
        if q_type == "pronunciation_odd_one" and not has_underline_markup(question.get("options")):
            errors.append(
                f"Question {question_id or container_id + '.' + str(question_index)} uses pronunciation_odd_one but options have no __underlined parts__."
            )
        if q_type in {"pronunciation_odd_one", "stress_odd_one"} and stem_text.strip():
            errors.append(
                f"Question {question_id or container_id + '.' + str(question_index)} uses {q_type} but has a per-question stem/prompt. "
                "Put one shared instruction in the question_group and render each item as number plus options only."
            )
        if q_type == "pronunciation_odd_one" and not pronunciation_underlines_are_consistent(question.get("options")):
            errors.append(
                f"Question {question_id or container_id + '.' + str(question_index)} uses pronunciation_odd_one but underlined letters are not the same across all options."
            )
        if q_type in {"pronunciation_odd_one", "stress_odd_one"} and option_texts_have_phrases(question.get("options")):
            errors.append(
                f"Question {question_id or container_id + '.' + str(question_index)} uses {q_type} but contains a phrase option. Phonetics options must be single words only."
            )
        if q_type == "stress_odd_one" and has_underline_markup(question.get("options")):
            errors.append(
                f"Question {question_id or container_id + '.' + str(question_index)} uses stress_odd_one but options contain underline markup."
            )
        if q_type in {"pronunciation_odd_one", "stress_odd_one"} and option_texts_have_embedded_labels(question.get("options")):
            errors.append(
                f"Question {question_id or container_id + '.' + str(question_index)} option text includes A./B./C. labels. Put labels in option.label or let the renderer add them."
            )
        if q_type == "odd_one_topic" and stem_text.strip():
            errors.append(
                f"Question {question_id or container_id + '.' + str(question_index)} uses odd_one_topic but repeats a per-question stem. "
                "Use one shared instruction in the question_group only."
            )
        if q_type in QUESTION_TYPES_WITH_OPTIONS and not question.get("options") and not question.get("items"):
            errors.append(f"Question {question_id} uses {q_type} but has no options/items.")

        if question_id and "answer" not in question and question_id not in answer_key:
            errors.append(f"Question {question_id} has no answer and is missing from answer_key.")

        points_each = as_number(container.get("points_each"), 0.0)
        calculated_points += as_number(question.get("points"), points_each)

    return total_questions, calculated_points


def validate_numbering(data: dict[str, Any], rendering: dict[str, Any], errors: list[str]) -> None:
    numbering = rendering.get("question_numbering")
    metadata = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}
    if numbering is None:
        numbering = "global" if metadata.get("document_profile") == "exam" else "per_section"

    if numbering == "global":
        numeric_ids = []
        for item in iter_questions(data):
            qid = question_id_for(item)
            _, number = question_sort_key(qid)
            if number >= 0:
                numeric_ids.append(number)
        if numeric_ids and numeric_ids != list(range(1, len(numeric_ids) + 1)):
            errors.append("Global numbering should be continuous from 1 to N.")
    elif numbering == "per_section":
        by_container: dict[str, list[int]] = {}
        for item in iter_questions(data):
            qid = question_id_for(item)
            _, number = question_sort_key(qid)
            if number >= 0:
                by_container.setdefault(str(item["container_id"]), []).append(number)
        for container_id, numbers in by_container.items():
            if numbers and numbers != list(range(1, len(numbers) + 1)):
                errors.append(f"Numbering in {container_id} should reset and run from 1 to N.")


def validate(data: dict[str, Any], kb_vocab_words: set[str] | None = None) -> list[str]:
    errors: list[str] = []
    metadata = validate_metadata(data, errors)
    rendering = validate_rendering(data, errors)
    validate_blocks(data, errors)
    validate_sections(data, errors)
    validate_multi_unit_structure(data, errors)
    validate_listening_transcript(data, errors)
    validate_phonetics_vocab(data, kb_vocab_words, errors)

    total_questions, calculated_points = validate_questions(data, errors)
    validate_matrix(data, errors, total_questions)
    validate_numbering(data, rendering, errors)

    metadata_total = as_number(metadata.get("total_points"), 0.0)
    if is_exam_like(metadata) and metadata_total and calculated_points and abs(metadata_total - calculated_points) > 0.05:
        errors.append(
            f"Calculated points ({calculated_points:g}) do not match metadata.total_points ({metadata_total:g})."
        )

    listening = data.get("listening")
    if isinstance(listening, dict):
        has_audio = bool(listening.get("audio_manifest"))
        if has_audio and not listening.get("transcript"):
            errors.append("listening.audio_manifest is present but listening.transcript is missing.")
    elif listening is not None:
        errors.append("listening must be an object when present.")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Path to assessment.json")
    parser.add_argument("--kb-db", type=Path, default=None, help="Optional knowledge_base.db path for strict phonetics word validation")
    parser.add_argument("--skip-kb-vocab-check", action="store_true", help="Skip KB-backed phonetics/stress option validation")
    parser.add_argument("--json", action="store_true", help="Print machine-readable validation result")
    args = parser.parse_args()

    try:
        errors = validate_artifact_path(args.input)
        data = load_json(args.input)
        kb_vocab_words = None
        if not args.skip_kb_vocab_check and not is_relative_to(args.input, REFERENCES_ROOT):
            kb_vocab_words = load_kb_vocab_words(args.kb_db or default_kb_db_path())
        errors.extend(validate(data, kb_vocab_words=kb_vocab_words))
    except Exception as exc:  # noqa: BLE001 - CLI should report concise validation failures.
        errors = [str(exc)]

    if args.json:
        print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    elif errors:
        print("Assessment JSON is invalid:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
    else:
        print("Assessment JSON is valid.")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
