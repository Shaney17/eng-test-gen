---
name: english-assessment-planner
description: Use first for any initial or underspecified request to create an English worksheet, practice sheet, quiz, or test for Vietnamese secondary-school teachers, such as "tạo phiếu bài tập lớp 6 unit 6" or "tạo đề kiểm tra". This skill must run before document generation unless the user already provides an approved blueprint/matrix. It queries the english-kb MCP, proposes a teacher-facing Vietnamese content plan, and finalizes a teacher-approved blueprint.
---

# English Assessment Planner

Use this skill before generating any worksheet, quiz, or test. The output of this skill is a clear Vietnamese plan for the teacher. Keep producer-only codes internal until generation starts.

Before showing the teacher-facing plan, build an internal plan JSON, validate it with `scripts/validate_assessment_plan.py`, fix any errors, then render the Vietnamese plan using `references/exercise_type_display_map.json` for the `Dạng bài` column.

## Routing Rule

- If the teacher only gives an initial creation request, such as "tôi muốn tạo phiếu bài tập cho unit 6, lớp 6", use this planner first.
- Do not generate DOCX, JSON, MP3, or full question content during planning.
- Move to `english-assessment-producer` only after the teacher approves the blueprint or provides an already-approved blueprint/matrix.
- If the teacher asks to "tạo luôn" but has not confirmed a structure, still produce a proposed blueprint and ask for confirmation before generation.

## Core Rules

- Always query the `english-kb` MCP before proposing content:
  - `get_unit_info` for grade/unit metadata and lesson structure.
  - `get_vocab` for unit vocabulary.
  - `get_grammar` for grammar points.
  - `get_matrices` when the teacher asks for a test or a reusable matrix.
  - `list_questions` only when reusing existing bank questions is useful.
- Do not invent unit vocabulary or grammar if the KB has relevant data.
- Keep the teacher-facing conversation in Vietnamese unless the teacher asks otherwise.
- Ask only for missing instructional decisions; do not ask for facts available from the KB.
- For tests, always produce a matrix summary before generation, but clarify whether the matrix is teacher-only metadata or printed in the DOCX.
- For worksheets, produce a lighter content frame with exercises, resource blocks, purpose, question types, and difficulty.
- If the teacher requests multiple units, keep the same exercise structure you would use for one unit. Do not create one separate exercise per unit. Mix vocabulary, grammar, and topics from all requested units inside each planned exercise.
- Treat the skill directory as read-only. Never create plan JSON, draft Markdown, DOCX, audio, or other generated artifacts under `skills/` or inside the installed skill folder. All generated files must go under `outputs/<slug>/` in the project/workspace.

## Default File Layout

When you need to persist planning artifacts, create a document-specific output folder and keep them next to the future assessment files:

```text
outputs/<slug>/
├── plan.json
├── blueprint.md
├── assessment.json        # created later by producer
├── <title>.docx           # created later by producer
└── audio/
    └── *.mp3
```

Use the skill folder only to read `SKILL.md`, `references/`, and `scripts/`.

## Planning Flow

1. Identify the document type:
   - worksheet / revision sheet / 15-minute quiz / midterm / end-of-unit test / custom test.
2. Identify curriculum scope:
   - grade, unit(s), lesson focus if needed, skills covered.
3. Query the KB and summarize usable source material:
   - unit title/topic, relevant vocab, grammar, reading/listening topic hints if available.
   - for multiple units, merge the usable source material into one combined pool grouped by content type, not into one worksheet section per unit.
4. Propose a structure:
   - section/exercise names, teacher-friendly exercise descriptions, count, difficulty, optional points, and layout notes.
5. Confirm constraints:
   - duration, total score, answer key required, transcript/audio if listening is included.
   - numbering mode: reset per exercise or continuous question numbering across the whole test.
   - output versions: student copy only, teacher copy with answers, or both.
6. Build an internal plan JSON using `references/plan_schema.json` and save it as `outputs/<slug>/plan.json` when a file is needed.
7. Validate it:
   - `python3 <skill_dir>/scripts/validate_assessment_plan.py outputs/<slug>/plan.json`
8. If validation fails, fix the plan JSON and validate again before replying.
9. Finalize a teacher-facing plan in the format below. If saving it, write `outputs/<slug>/blueprint.md`, not a file in `skills/`.

## Internal Plan JSON

Use this structure internally. Do not show this JSON to the teacher unless explicitly requested.

```json
{
  "document_type": "worksheet",
  "grade": 7,
  "units": [{"unit_number": 9, "title": "Festivals around the world"}],
  "title_header": "Grade 7 - Unit 9 Worksheet",
  "duration": "35-45 phút",
  "total_points": null,
  "output_language": "Tiếng Anh, chỉ dẫn ngắn gọn",
  "numbering": "per_section",
  "matrix_printed_in_docx": false,
  "output_versions": ["student", "teacher_answer_key"],
  "sections": [
    {
      "section": "A",
      "focus": "Vocabulary",
      "exercise_type": "vocab_mcq",
      "teacher_facing_format": "MCQ từ vựng trong ngữ cảnh tiếng Anh",
      "difficulty": 1,
      "count": 6,
      "points": 1.5,
      "layout_notes": "Đáp án A/B/C/D dàn đều trên một dòng"
    }
  ],
  "content_sources": {
    "vocabulary": [],
    "grammar": [],
    "reading_listening_topic": ""
  },
  "special_requirements": {
    "listening": false,
    "transcript": false,
    "audio": false,
    "notes": ""
  }
}
```

Rules for internal JSON:

- `exercise_type` must be one of the keys in `references/exercise_type_display_map.json`.
- `teacher_facing_format`, when present, must equal the exact mapped value from `references/exercise_type_display_map.json`.
- The visible `Dạng bài` column must come from the display map, not from free writing.
- Never use broad labels such as `Đọc và chọn đáp án`, `MCQ`, `TF`, `Yes/No`, `fill_blank`, or `writing`.
- Keep `Yes/No questions` only as grammar content/focus, never as `exercise_type` or visible exercise format.

## Blueprint Format

Return a concise Markdown blueprint with this structure:

```markdown
## Kế hoạch phiếu/đề

- Loại tài liệu:
- Lớp:
- Unit/phạm vi:
- Tiêu đề/đầu trang:
- Thời lượng:
- Tổng điểm:
- Ngôn ngữ hiển thị:
- Cách đánh số:
- In ma trận trong file Word:
- Phiên bản đầu ra:

| Phần | Trọng tâm | Dạng bài | Mức độ | Số câu | Điểm | Ghi chú trình bày |
|---|---|---|---:|---:|---:|---|

### Nguồn nội dung
- Từ vựng:
- Ngữ pháp:
- Chủ đề đọc/nghe:

### Yêu cầu riêng
- Bài nghe:
- Bản chép lời:
- File nghe:
- Ghi chú:
```

Do not add any extra section after `Yêu cầu riêng`. In particular, do not print a final `Cấu trúc bài tập`, `Cấu trúc đề`, summary of sections, internal mapping, or technical transfer block. The exercise structure is already captured in the main table.

## Supported Values

- `knowledge_type`: `vocabulary`, `grammar`, `reading`, `listening`, `writing`, `speaking`, `mixed`
- In teacher-facing tables, do not show raw `exercise_type` codes. Use short descriptions such as "MCQ in English context", "Complete sentences with words from a box", "Give the correct verb form", "Rewrite sentences", or "Read and choose T/F".
- `exercise_type` codes are internal only. Do not print them in the teacher-facing plan.
- For the `Dạng bài` column, use only exact values from `references/exercise_type_display_map.json`.
- `difficulty`: `1` easy, `2` medium, `3` hard
- `question_numbering`: `per_section`, `global`
- For worksheets/revision sheets, `total_points` and section `points` may be `null` or shown as `Không chấm điểm`; do not force point totals.
- For quizzes/tests/exams, keep `total_points` and section points consistent.

## Exercise Format Reference

Read `references/exercise_formats.md` when choosing or explaining exercise formats. It includes common Vietnamese secondary-school English formats and example layouts for pronunciation, vocabulary, grammar, communication, reading, listening, writing, and speaking.

Treat `references/exercise_formats.md` as a closed allowlist. Do not propose formats outside it. In particular, do not propose `Yes/No` or `meaning_matching`; use the replacements listed in the reference.

Vocabulary MCQ means English-context MCQ only. Do not propose EN-VI or VI-EN meaning translation questions.

Do not write "Yes/No" in the teacher-facing `Exercise format` column. It is allowed in `Grammar focus` only when it comes from the unit grammar in `get_grammar`.

- Exercise format: `MCQ ngữ pháp`
- Grammar focus: `Yes/No questions`

Internally, use `grammar_mcq` or `question_making`; never use `Yes/No` as a format name or `exercise_type`.

When talking to teachers, describe the format briefly in natural Vietnamese/English instead of showing the code. Examples:

| Producer code | Teacher-facing wording |
|---|---|
| `vocab_mcq` | MCQ từ vựng trong ngữ cảnh tiếng Anh |
| `word_bank_gap_fill` | Điền từ vào câu/đoạn với word bank |
| `grammar_mcq` | MCQ ngữ pháp |
| `verb_form` | Chia dạng đúng của động từ trong ngoặc |
| `word_form` | Cho dạng đúng của từ trong ngoặc |
| `grammar_gap_fill` | Điền cấu trúc/ngữ pháp phù hợp vào chỗ trống |
| `question_making` | Đặt câu hỏi cho phần gạch chân / theo gợi ý |
| `sentence_rewrite` | Viết lại câu sao cho nghĩa không đổi |
| `rewrite_with_given_word` | Viết lại câu dùng từ cho sẵn |
| `sentence_building` | Dùng từ gợi ý viết thành câu hoàn chỉnh |
| `reading_mcq` | Đọc hiểu và trả lời câu hỏi MCQ |
| `reading_gap_fill` | Đọc đoạn văn và chọn từ điền vào chỗ trống |
| `reading_tf` | Đọc đoạn văn và điền T/F/NG |
| `guided_paragraph` | Viết đoạn văn ngắn theo gợi ý |
| `listening_mcq` | Nghe và chọn đáp án đúng |

When planning, specify these constraints in natural language where relevant:
- Reading T/F is always T/F/NG, with students writing the answer themselves.
- Reading MCQ has two separate formats: `reading_mcq` for comprehension questions and `reading_gap_fill` for cloze blanks. Do not merge them under one generic "đọc và chọn đáp án" label.
- For `reading_gap_fill`, do not plan a word bank; each blank has A/B/C/D options.
- Rewrite with given word must include the cue word.
- Rewrite formats should include an answer prompt, usually the first 1-2 words of the rewritten sentence.
- Question-making and pronunciation formats need underlined parts.
- Stress questions do not need and should not use underlined parts.
- Phonetics/stress options must be single words only, not phrases.
- In pronunciation items, the underlined letters must be identical across all options.
- Question-making needs a blank answer line under each item.

## Matrix Guidance

- For worksheets/revision sheets, do not validate or force point totals unless the teacher explicitly asks for grading.
- For quizzes/tests/exams, keep total points consistent with the teacher's requested scale, usually 10.
- If the teacher does not specify point values for a quiz/test/exam, assign simple equal or near-equal points and state the assumption.
- For 15-minute tests, prefer compact sections and objective questions.
- For longer tests, include skill balance when requested: vocabulary/grammar plus reading and/or listening/writing.
- If listening is included, require transcript in the producer output and mark audio as optional until teacher confirms.
- Listening transcripts belong in the answer key/transcript section only, not in the student question area.
- A listening exercise should use one shared listening text/audio source for all questions in that exercise. Do not plan a separate dialogue or transcript per listening question.
- For exam papers, use continuous `Question 1...N` numbering unless the teacher explicitly asks otherwise.
- For worksheets, reset numbering inside each exercise unless the teacher asks for continuous numbering.
- For exam papers, default to not printing the matrix in the student DOCX; keep it in JSON for teacher review.
- For worksheets, include supporting blocks when useful, such as vocabulary tables, word banks, crossword grids, and reading passages.

## After Teacher Approval

When the teacher confirms the plan, switch to `english-assessment-producer`. Do not show a separate technical transfer section to the teacher. Keep the approved plan, grade/unit scope, KB-derived vocab/grammar constraints, numbering mode, output versions, and listening/audio requirements as internal context for generation.
