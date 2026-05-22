---
name: english-assessment-producer
description: Use only after an English worksheet/test blueprint has been explicitly approved, or when revising/rendering an existing assessment.json. Do not use for an initial vague request like "tạo phiếu bài tập lớp 6 unit 6"; route that to english-assessment-planner first. This skill creates block-based assessment.json, renders worksheet or exam DOCX, maintains answer keys/listening transcripts, and prepares or calls ElevenLabs audio generation when confirmed.
---

# English Assessment Producer

Use this skill after the teacher has approved an assessment blueprint. It owns the production artifact: `assessment.json`, DOCX output, answer key, listening transcript, audio manifest, and targeted revisions.

## Entry Gate

Before generating or rendering anything, check whether one of these is present:

- an explicit `APPROVED ASSESSMENT BLUEPRINT` handoff from `english-assessment-planner`;
- a teacher-approved matrix/blueprint in the conversation;
- an existing `assessment.json` that the teacher wants revised or rerendered.

If none is present, stop production and route to `english-assessment-planner`. Do not infer the whole structure from only grade/unit/document type. For example, "tôi muốn tạo phiếu bài tập cho unit 6, lớp 6" is a planning request, not a production request.

## Core Rules

- Never create DOCX/JSON/MP3 from an initial request that has no approved blueprint.
- Use the confirmed blueprint as the source of truth for document profile, blocks, question groups, counts, difficulty, and points. For worksheets/revision sheets, points are optional unless the teacher explicitly requested grading.
- Query `english-kb` before generating content for a grade/unit:
  - `get_unit_info`, `get_vocab`, `get_grammar`;
  - `list_questions` if reusable bank questions exist;
  - `add_questions` and `mark_used` only after the teacher finalizes and explicitly wants bank tracking.
- Keep a JSON source next to every DOCX. Never treat the DOCX as the primary editable source.
- When revising, update only the requested block/group/question in JSON, then validate and render again.
- Always include an answer key at the end of the DOCX.
- If the assessment includes listening, always include transcript; generate MP3 only after teacher confirmation.
- For multi-unit worksheets/tests, preserve the approved exercise structure as normal skill/format sections. Do not create one separate exercise per unit; mix KB-derived vocabulary, grammar, and topics from all requested units inside each exercise.

## Default File Layout

```text
outputs/<slug>/
├── assessment.json
├── <title>.docx
└── audio/
    └── *.mp3
```

DOCX rendering always uses the built-in rules in `references/format_rules.md`. Do not require a `.docx` template file. Resolve script/reference paths relative to this skill folder.

Bundled files:

```text
english-assessment-producer/
├── SKILL.md
├── scripts/
│   ├── validate_assessment_json.py
│   ├── render_assessment_docx.py
│   └── generate_listening_audio.py
└── references/
    ├── sample_assessment.json
    ├── sample_block_worksheet.json
    ├── sample_block_exam.json
    ├── sample_audio_manifest.json
    ├── exercise_formats.md
    └── format_rules.md
```

## Assessment JSON Shape

Use a stable, explicit block-based structure. Legacy `sections` are still acceptable for simple worksheets, but new documents should use `blocks`.

```json
{
  "metadata": {
    "title": "Grade 7 Unit 1 Worksheet",
    "document_type": "worksheet",
    "document_profile": "worksheet",
    "grade": 7,
    "units": [{"unit_number": 1, "title": "HOBBIES"}],
    "duration_minutes": 45,
    "total_points": 10,
    "student_fields": ["Name", "Class"],
    "exam_code": "000"
  },
  "rendering": {
    "question_numbering": "per_section",
    "print_matrix": false,
    "include_answer_key": true,
    "include_transcript": true,
    "option_layout": "auto"
  },
  "header": {
    "left": ["PHÒNG GD&ĐT ...", "TRƯỜNG ..."],
    "right": ["KIỂM TRA CUỐI KỲ", "MÔN: TIẾNG ANH", "Thời gian làm bài: 45 phút"]
  },
  "matrix": [
    {
      "section_id": "A",
      "title": "Vocabulary",
      "knowledge_type": "vocabulary",
      "exercise_type": "vocab_mcq",
      "difficulty": 1,
      "count": 5,
      "points_each": 0.2
    }
  ],
  "blocks": [
    {
      "type": "vocabulary_table",
      "id": "A",
      "title": "Vocabulary",
      "columns": ["ENGLISH", "TYPE", "PRONUNCIATION", "VIETNAMESE"],
      "rows": [["unusual", "adj", "/ʌnˈjuːʒuəl/", "khác thường"]]
    },
    {
      "type": "question_group",
      "id": "B",
      "title": "Exercise 1",
      "instructions": "Choose the best answer.",
      "knowledge_type": "vocabulary",
      "exercise_type": "vocab_mcq",
      "difficulty": 1,
      "points_each": 0.2,
      "numbering": "per_section",
      "option_layout": "inline",
      "questions": [
        {
          "id": "A1",
          "stem": "My brother has an ________ hobby: he collects old bus tickets.",
          "options": ["unusual", "outdoor", "valuable", "patient"],
          "answer": "A",
          "explanation": "unusual fits the context of a hobby that is not common."
        }
      ]
    }
  ],
  "answer_key": [{"question_id": "A1", "answer": "A"}],
  "listening": {
    "transcript": "",
    "audio_manifest": null
  }
}
```

## Supported Blocks

- `heading`: section heading or part heading.
- `text`: short instruction/prose paragraph.
- `vocabulary_table`: word list with English/type/pronunciation/Vietnamese columns.
- `word_bank`: compact table of available words/phrases.
- `crossword`: grid table; use empty strings for blank cells.
- `notice_box`: announcement/sign/notice content in a bordered box.
- `passage`: reading/listening passage before questions.
- `question_group`: instruction plus questions, with optional shared passage/notice/sign.

For exam-like papers, prefer `question_group` blocks with global numbering and do not print the matrix in the student copy. For worksheet-like papers, use multiple blocks/exercises and reset numbering per exercise.

## Exercise Format Reference

Read `references/exercise_formats.md` before generating a new assessment. It defines common Vietnamese secondary-school English exercise formats, stable `exercise_type` names, and example JSON/text layouts.

Treat `references/exercise_formats.md` as a closed allowlist. If the blueprint or generated JSON contains an unknown format such as `Yes/No` or `meaning_matching`, normalize it to an allowed format before rendering or ask the teacher to approve a supported replacement.

Vocabulary MCQ must be English-context questions only. Do not generate EN-VI or VI-EN meaning translation questions such as "Which word means...?".

Do not use "Yes/No" as `exercise_type` or as the visible exercise format label. It is allowed as grammar content/focus when it came from the planner or KB, while keeping `exercise_type` as `grammar_mcq` or `question_making`.

Rendering constraints:
- Do not put visible numbering such as `Question 1.` or `1.` inside `stem`; keep numbering in the renderer/display label only.
- Do not repeat the section instruction inside each question stem.
- `reading_tf` means T/F/NG. Do not include A/B/C options; students write T, F, or NG in the blank.
- Reading MCQ must be split into two formats: `reading_mcq` for reading comprehension questions and `reading_gap_fill` for cloze blanks with MCQ options.
- For `reading_gap_fill`, do not create a `word_bank`; render each blank item as the question number plus A/B/C/D options on the same line.
- `sentence_rewrite` and `rewrite_with_given_word` must include a student answer prompt, usually with the first 1-2 words of the rewritten sentence.
- `rewrite_with_given_word` must include `given_word`/`cue_word` or the cue word in parentheses.
- `word_bank_gap_fill` must use a separate `word_bank` block immediately before its `question_group`; do not place the word bank after questions or far away from the exercise heading.
- Use `__underlined text__` markup for underlined sounds/phrases in `pronunciation_odd_one` options and `question_making` stems.
- Do not use underline markup in `stress_odd_one`; stress questions compare word stress, not underlined sounds.
- `pronunciation_odd_one` and `stress_odd_one` options must be single words only, not phrases.
- In `pronunciation_odd_one`, the underlined letters must be identical across all options, such as `scholar`, `aching`, `chemist`, `approach` all underlining `ch`.
- `pronunciation_odd_one`, `stress_odd_one`, and `odd_one_topic` must have one shared instruction in the `question_group`; individual questions should contain only options and answer. Do not put target sounds such as `ee` or repeated prompts like `Choose the odd one out` in each question stem.
- Listening question groups must not include the transcript as a `passage`, `text`, question `passage`, or visible stem/prompt. Put the full transcript only in top-level `listening.transcript`; the renderer prints it after the answer key.
- Dialogue transcripts must be line-broken by turn: `Mai: ...\nNam: ...`, not `Mai: ... Nam: ...` in one paragraph.
- `question_making` must leave a blank answer line for students; set `lines` to at least `1` when generating JSON.

## Production Flow

1. Generate `assessment.json` from the confirmed blueprint and KB data.
2. Run validation:
   - `python3 <skill_dir>/scripts/validate_assessment_json.py outputs/<slug>/assessment.json`
3. Render DOCX:
   - `python3 <skill_dir>/scripts/render_assessment_docx.py --input outputs/<slug>/assessment.json --output outputs/<slug>/<title>.docx`
4. For listening audio after teacher confirmation:
   - create or update `listening.audio_manifest`;
   - run `python3 <skill_dir>/scripts/generate_listening_audio.py --manifest outputs/<slug>/audio_manifest.json --out-dir outputs/<slug>/audio`.

Use the JSON examples in `references/` when you need the exact block schema for worksheets, exams, legacy section-based files, or audio manifests.

Always use `references/format_rules.md` when rendering DOCX. It contains extracted formatting rules from the worksheet and exam sample files, including font, spacing, bolding, title/header/footer, tables, and template selection.

## Revision Flow

- Locate the requested block/question by `block.id`, `question.id`, or visible question number.
- Change only the requested JSON node and any directly dependent fields:
  - answer key;
  - transcript;
  - audio manifest text/voice mapping.
- Re-run validation and render DOCX again.
- Summarize exactly what changed.

## Listening Audio Manifest

Single narration:

```json
{
  "items": [
    {
      "id": "listening-1",
      "mode": "single",
      "text": "Hello. My name is Mai...",
      "voice_id": "VOICE_ID",
      "model_id": "eleven_multilingual_v2",
      "output_file": "listening-1.mp3"
    }
  ]
}
```

Dialogue:

```json
{
  "items": [
    {
      "id": "dialogue-1",
      "mode": "dialogue",
      "model_id": "eleven_v3",
      "output_file": "dialogue-1.mp3",
      "turns": [
        {"speaker": "Mai", "text": "What is your hobby?", "voice_id": "VOICE_ID_1"},
        {"speaker": "Nam", "text": "I like making models.", "voice_id": "VOICE_ID_2"}
      ]
    }
  ]
}
```

## Quality Bar

- Question count matches the matrix. Point totals must match for quizzes/tests/exams; worksheets may omit or loosely specify points unless grading was requested.
- Distractors are plausible and age-appropriate.
- Reading/listening passages stay aligned with unit topic and student level.
- Answer key is complete and consistent with question IDs.
- Transcript is printable and can stand alone even if MP3 generation is skipped.
