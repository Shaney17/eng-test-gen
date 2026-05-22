# DOCX Format Rules For English Worksheets And Exams

These rules are extracted from two sample files:

- Worksheet sample: `HT7-U9-future transport.docx`
- Exam sample: `KT-CK2-Anh8-25-26.docx`

Do not store or require the sample DOCX files. Use these rules to render new DOCX files without installing templates per repo.

## Template Selection

Use `worksheet_practice` for worksheets, revision sheets, homework sheets, and topic practice.

Use `exam_official` for midterm/final tests, quizzes with school/exam metadata, and papers requiring exam code, student fields, and footer page numbering.

## Shared Typography

- Primary font: Times New Roman.
- Body font size: 12 pt.
- Body line spacing: single (`1.0`) or near single (`1.0-1.08`).
- Paragraph spacing: compact; normally 0 pt before and 0-2 pt after.
- Use bold for headings, exercise labels, question labels, and option labels.
- Avoid decorative colors. Use black text.
- Use tabs for compact inline options when space permits.

## `worksheet_practice` Rules

Extracted from `HT7-U9-future transport.docx`.

### Page Setup

- Page size: approximately 211.67 mm x 273.93 mm.
- Margins are very compact:
  - Top: about 7.5 mm.
  - Bottom: about 5 mm.
  - Left: about 7.7 mm.
  - Right: about 6.5 mm.
- No header.
- No footer.
- Dense layout is acceptable; prioritize fitting exercises on fewer pages.

### Font And Paragraphs

- Use Times New Roman, 12 pt for most text.
- Main title may be 14-16 pt and bold.
- Most body paragraphs are left aligned.
- Use compact spacing:
  - line spacing: 1.0 or 1.15;
  - before/after: 0 pt for ordinary questions;
  - add about 4-5 pt before major exercise headings if needed.
- Question paragraphs commonly use hanging indents:
  - common left indent around 14 pt, first-line indent around -14 pt;
  - for longer exercise lists, hanging indent around 21 pt / -7 pt may appear.

### Title And Headings

- First line format: `TOPIC <number>: <TOPIC TITLE>`.
- Title is bold; topic title uppercase.
- Major sections use Roman numerals and uppercase:
  - `I. VOCABULARY`
  - `III. GRAMMAR`
  - `PHONETICS`
  - `VOCABULARY AND GRAMMAR`
- Exercise headings start with `Exercise <number>:` and are bold at least through `Exercise <number>:`. The instruction text may also be bold when short.

### Worksheet Block Order

Typical order:

1. Topic title.
2. Optional vocabulary table.
3. Major section heading.
4. `PRACTICE:`.
5. Exercise heading.
6. Resource block if any, such as crossword or word bank.
7. Questions.
8. Next exercise.
9. Answer key only in teacher version or final section.

### Vocabulary Table

- Table columns: `ENGLISH | TYPE | PRONUNCIATION | VIETNAMESE`.
- Header row should be bold.
- Table can use full available width.
- Borders: visible grid.
- Autofit is acceptable.
- Body text: Times New Roman, 12 pt.

### Crossword

- Use a grid table.
- Center the table.
- Fixed/autofit disabled if possible.
- Each cell contains one letter, number, or blank.
- Visible borders.
- Keep cells compact and square-like.

### Word Bank

- Use a compact table, usually 2 rows x 4 columns for 8 words.
- Visible borders.
- Text centered or lightly left aligned.
- Place immediately after the exercise heading and before questions.

### Questions And Options

- Worksheet numbering resets per exercise: `1.`, `2.`, `3.`.
- Question number and question text are separated by one normal space, not a tab.
- MCQ options may be on one line separated by tabs:
  - `A. option    B. option    C. option`
- Render MCQ options with even horizontal spacing. Prefer a no-border table: A/B/C/D on one row for short options, A/B on the first row and C/D on the second row for long options.
- For three-option worksheet MCQ, A-C is acceptable.
- For writing/rewrite questions, use long underline answer spaces.
- Do not repeat the section instruction inside each question. If the exercise heading says `Choose the word that has a different sound pattern from the others`, each question should show only the item number and options, not the same instruction again.
- Do not put `Question 1.` or `1.` inside the question stem; numbering is rendered separately.
- Reading True/False comprehension must be T/F/NG with a blank line/space for students to fill, not A/B/C choices.
- Reading MCQ is split into two formats: comprehension Q&A (`reading_mcq`) and cloze blank-filling (`reading_gap_fill`). Do not use one generic reading MCQ label for both.
- Reading cloze blank-filling (`reading_gap_fill`) must not have a word bank; render the question number and A/B/C/D options on the same line, like phonetics.
- Render underlined sounds/phrases using real Word underline. Source JSON uses `__underlined text__`.
- Stress questions do not use underlines.
- Phonetics and stress options must be single words only, not phrases.
- Pronunciation odd-one-out options must underline the same letters in every option; do not mix `u`, `o`, and `i` in one item.
- In phonetics tables, the question-number column should be only wide enough for about three characters, such as `10.`; give the remaining width to answer options.
- Rewrite-with-given-word questions must show the cue word, usually in parentheses after the original sentence.
- Rewrite questions must show a student answer prompt on the next line, usually starting with the first 1-2 words of the rewritten sentence.
- Question-making items must have an answer line under each question.

## `exam_official` Rules

Extracted from `KT-CK2-Anh8-25-26.docx`.

### Page Setup

- Page size: A4, approximately 210 x 297 mm.
- Margins:
  - Top: 10 mm.
  - Bottom: 11 mm.
  - Left: 20 mm.
  - Right: 10 mm.
- Use one section unless explicitly needed.

### Header Area

Use a 1-row, 2-column table at the top.

Left cell:

```text
SỞ/PHÒNG GD&ĐT ...
TRƯỜNG ...

--------------------
(Đề thi có ___ trang)
```

Right cell:

```text
KIỂM TRA ...
NĂM HỌC ...
MÔN: ...
Thời gian làm bài: ___ phút
(không kể thời gian phát đề)
```

Formatting:

- Both cells centered.
- Right cell title lines bold.
- Keep compact line spacing.
- Table has no obvious heavy styling; use clean layout, minimal or no borders if the renderer supports it.

### Student Info Row

Use a 1-row, 3-column table:

```text
Họ và tên: ........................................
Số báo danh: .......
Mã đề 000
```

Formatting:

- Compact row.
- Text 12 pt.
- Keep it directly below the header table.

### Footer

Footer format:

```text
Mã đề 000    Page X/Y
```

- Right aligned.
- 12 pt.
- Use page number fields when possible.

### Font And Paragraphs

- Body font size: 12 pt.
- Body line spacing: mostly 1.0.
- Paragraph spacing:
  - ordinary question/options: 0 pt before, 0-2 pt after;
  - section instructions: 0-4 pt after;
  - occasional section transition: about 3 pt before and 2 pt after.
- Many reading paragraphs are justified.
- Avoid large blank gaps between question groups.

### Section Instructions

- Instructions are prose lines, often bold at the beginning or fully bold for short instructions.
- Typical wording:
  - `Mark the letter A, B, C or D to indicate ...`
  - `Read the following passage and mark ...`
  - `You will hear ... You will listen TWICE.`
- Do not use decorative headings; exam sections are mostly instruction paragraphs.

### Questions

- Use global numbering throughout the paper:
  - `Question 1.`
  - `Question 2.`
- `Question N.` is bold.
- Stem text follows on the same line when short.
- Options labels `A. B. C. D.` are bold.
- Option text itself is not bold unless the source specifically requires emphasis.
- Use four options for exam MCQ unless the approved blueprint says otherwise.
- Do not repeat generic section instructions as each question stem. For pronunciation/stress items, the instruction appears once before the group; each item should show `Question N.` plus options.

### Option Layout

Use compact inline options when short:

```text
A. travel    B. plane    C. camp    D. backpack
```

Use two-line/two-column style when options are long:

```text
A. Their cooking skills       B. Their weaving skills
C. Their farming practices    D. Their boat-building skills
```

Use stacked options when options are sentence-length.

### Notice / Announcement / Sign Boxes

- Use a 1-cell table with visible border.
- Text can be uppercase and centered for signs/notices.
- Place the box immediately after the instruction and before the questions.
- Keep compact internal spacing.

### Reading Passages

- Body text can be justified.
- Keep paragraphs compact.
- Passage appears before related questions.
- Do not put answer key in student exam copy.

### Images

- The exam sample contains one drawing/image. If using sign/image prompts, keep them inline with the question group and avoid oversized images.

## Bold Rules

Use bold for:

- worksheet main title and major section headings;
- worksheet `Exercise <number>:` labels;
- exam header title lines;
- exam question labels: `Question N.`;
- exam option labels: `A.`, `B.`, `C.`, `D.`;
- short instruction lead-ins such as `Mark the letter A, B, C or D`.

Do not bold long reading passages or ordinary answer choices unless matching the compact exam style with bold option labels only.

## Answer Key And Teacher Copy

- Student worksheet may omit answer key; teacher version includes answer key at the end.
- Student exam should omit answer key.
- Teacher exam version can include answer key after a page break or in a separate file.
- Listening transcript should be included in teacher version, not necessarily in student version.

## Rendering Defaults

If no teacher-provided DOCX template exists:

- For `document_profile = worksheet`, apply `worksheet_practice`.
- For `document_profile = exam`, apply `exam_official`.
- Use the teacher-provided metadata to fill school, exam name, subject, duration, and exam code.
- Keep output clean and compact; these are utilitarian school documents, not decorative handouts.
