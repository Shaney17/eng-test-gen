# Common English Exercise Formats In Vietnamese Secondary Schools

Use these formats when generating `assessment.json`. This is a closed taxonomy: keep `exercise_type` stable and use exactly the names listed here. Do not invent variants.

Forbidden labels and replacements:

- `Yes/No`, `yes_no`, `yes-no` -> use `reading_tf`, `listening_tf`, or `short_answer`.
- `meaning_matching`, `meaning matching` -> not allowed. Use English-context `vocab_mcq` instead.
- `true_false` -> use `reading_tf` or `listening_tf`.
- `fill_blank` -> use `word_bank_gap_fill`, `grammar_gap_fill`, `reading_gap_fill`, or `listening_gap_fill`.

Do not use "Yes/No" as `exercise_type` or as the visible exercise format label. It is allowed as grammar content/focus when it came from the planner or KB. Keep `exercise_type` as `grammar_mcq` or `question_making`.

Allowed `exercise_type` values:

```text
pronunciation_odd_one
stress_odd_one
vocab_mcq
matching
word_bank_gap_fill
missing_letters
word_form
odd_one_topic
label_picture
crossword
grammar_mcq
verb_form
grammar_gap_fill
choose_between_forms
error_correction
sentence_rewrite
rewrite_with_given_word
sentence_combining
sentence_building
question_making
dialogue_completion
dialogue_ordering
speaking_card
reading_mcq
reading_tf
reading_gap_fill
short_answer
heading_matching
reference_word
closest_opposite_meaning
notice_reading
sentence_ordering
sentence_insertion
listening_mcq
listening_tf
listening_gap_fill
listening_table_completion
listening_matching
guided_sentence_writing
guided_paragraph
email_writing
picture_prompt_writing
word_form_writing
```

## Pronunciation / Phonetics

### `pronunciation_odd_one`
Instruction: `Choose the word whose underlined part is pronounced differently from the others.`

Mark the pronounced part with `__underlined text__`; the renderer converts it to Word underline. Use one shared `question_group.instructions` value and do not repeat the instruction inside each question stem. Each question should omit `stem`/`prompt`; do not put the target sound (`ee`, `ch`, `/i:/`, etc.) before the options. Each option must be one real English word from the KB vocabulary only, not a phrase; use `dance`, not `folk dance`, and never invent pseudo-words. The underlined letters must be identical across all options, for example all four options underline `ch`.

```json
{
  "type": "question_group",
  "exercise_type": "pronunciation_odd_one",
  "instructions": "Choose the word whose underlined part is pronounced differently from the others.",
  "questions": [
    {
      "id": "Q1",
      "options": ["c__i__ty", "b__i__cycle", "r__i__ce", "v__i__llage"],
      "answer": "D"
    }
  ]
}
```

### `stress_odd_one`
Instruction: `Choose the word that has a different stress pattern from the others.`

Do not underline any letters in stress questions. Each option must be one real English word from the KB vocabulary only, not a phrase or invented pseudo-word.

```json
{"id": "Q1", "options": ["historic", "exciting", "expensive", "beautiful"], "answer": "D"}
```

## Vocabulary

### `vocab_mcq`
```text
Question 1. Tet is a time for family ________.
A. gatherings    B. maps    C. buildings    D. robots
```

JSON:

```json
{"id": "Q1", "stem": "Tet is a time for family ________.", "options": ["gatherings", "maps", "buildings", "robots"], "answer": "A"}
```

### `matching`
Use `items` with `left` and `right`.

```json
{
  "exercise_type": "matching",
  "questions": [
    {
      "id": "Q1",
      "stem": "Match the words with their meanings.",
      "items": [
        {"left": "decorate", "right": "make something look more attractive"},
        {"left": "benefit", "right": "a good or useful effect"}
      ],
      "answer": "1-b, 2-a"
    }
  ]
}
```

Use this only when the approved blueprint explicitly asks for matching. Do not use meaning-translation matching.

### `word_bank_gap_fill`
Use a separate `word_bank` block immediately before the question group when the word list should be visible as a box/table. Do not place it after questions or separated from the exercise by another block.

```json
{
  "type": "word_bank",
  "words": ["decorate", "benefit", "outdoor", "patient"],
  "columns_count": 4
}
```

```text
1. We often ________ our house before Tet.
2. Gardening is an ________ activity.
```

### `missing_letters`
```json
{"id": "Q1", "stem": "I will catch the t_ _ _ _ from Ha Noi to Ho Chi Minh City.", "answer": "train"}
```

### `word_form`
```json
{"id": "Q1", "stem": "My sister is very ________ when she waits for the bus. (PATIENCE)", "answer": "patient"}
```

### `odd_one_topic`
Use one shared `question_group.instructions` value: `Choose the odd one out.` Each question should omit `stem`/`prompt` and contain only options plus answer.

```json
{"id": "Q1", "options": ["train", "bus", "plane", "kitchen"], "answer": "D"}
```

### `label_picture`
Use a `picture_prompt` block when image support is available; otherwise use textual picture labels.

```text
Picture 1: __________
Picture 2: __________
```

### `crossword`
Use a `crossword` block for the grid and a `question_group` for clues.

```json
{
  "type": "crossword",
  "grid": [["", "1", "T", "R", "A", "I", "N"], ["2", "", "", "", "", "", ""]]
}
```

## Grammar

### `grammar_mcq`
```json
{"id": "Q1", "stem": "You ________ make noise in the library.", "options": ["should", "shouldn't", "can", "are"], "answer": "B"}
```

### `verb_form`
```json
{"id": "Q1", "stem": "My father ________ TV every evening. (watch)", "answer": "watches"}
```

### `grammar_gap_fill`
```json
{"id": "Q1", "stem": "There is ________ orange on the table.", "answer": "an"}
```

### `choose_between_forms`
```json
{"id": "Q1", "stem": "I think people will use / are using flying cars in the future.", "answer": "will use"}
```

### `error_correction`
```json
{"id": "Q1", "stem": "She go to school by bus every day.", "answer": "go -> goes"}
```

### `sentence_rewrite`
```json
{
  "id": "Q1",
  "stem": "The new phone is cheaper than the old phone.",
  "prompt": "The old phone is __________________________________________.",
  "answer": "The old phone is more expensive than the new phone.",
  "lines": 1
}
```

### `rewrite_with_given_word`
```json
{
  "id": "Q1",
  "stem": "The weather today is not as hot as yesterday. (THAN)",
  "given_word": "THAN",
  "prompt": "Yesterday ________________________________________________.",
  "answer": "Yesterday was hotter than today.",
  "lines": 1
}
```

### `sentence_combining`
```json
{"id": "Q1", "stem": "I was tired. I finished my homework. (ALTHOUGH)", "answer": "Although I was tired, I finished my homework.", "lines": 1}
```

### `sentence_building`
```json
{"id": "Q1", "stem": "We / visit / grandparents / next Sunday.", "answer": "We will visit our grandparents next Sunday.", "lines": 1}
```

### `question_making`
```json
{"id": "Q1", "stem": "Nam goes to school __by bike__.", "answer": "How does Nam go to school?", "lines": 1}
```

## Communication / Speaking Support

### `dialogue_completion`
```json
{
  "id": "Q1",
  "stem": "Tourist: Could you tell me the way to the museum? Local: ________",
  "options": ["Go straight, then turn left.", "I am fine.", "No, I don't.", "It is mine."],
  "answer": "A"
}
```

### `dialogue_ordering`
```json
{
  "id": "Q1",
  "stem": "Put the dialogue lines in the correct order.",
  "items": ["a. Yes, I do.", "b. What is your favourite programme?", "c. Do you like watching TV?"],
  "answer": "c-a-b"
}
```

### `speaking_card`
Use a `rubric` block if adding scoring criteria.

```text
Topic: Your neighbourhood
- Where do you live?
- What places are near your house?
- What do you like about it?
```

## Reading

### `reading_mcq`
Use `passage` on the group for shared reading text. This format is for reading comprehension questions only: each `stem` asks a question about the passage and has answer options. Do not use `reading_mcq` for blank-filling items.

```json
{
  "type": "question_group",
  "exercise_type": "reading_mcq",
  "passage": "Millions of people like travelling...",
  "questions": [
    {"id": "Q1", "stem": "What is the passage mainly about?", "options": ["Travelling", "Robots", "Sports", "Food"], "answer": "A"}
  ]
}
```

### `reading_tf`
```json
{"id": "Q1", "stem": "Mai visited her grandparents last weekend.", "answer": "T"}
{"id": "Q2", "stem": "Mai travelled there by train.", "answer": "NG"}
```

Use T/F/NG for reading comprehension. Do not include `options`; students write T, F, or NG in a blank.

### `reading_gap_fill`
Use this for cloze reading: a passage or sentence contains numbered blanks, and each question provides MCQ options for one blank. Do not use `reading_gap_fill` for comprehension questions. Do not add a separate `word_bank` block; each blank already has A/B/C/D options.

```json
{"id": "Q1", "stem": "People often (1) ________ their houses before Tet.", "options": ["decorate", "visit", "watch", "play"], "answer": "A"}
```

### `short_answer`
```json
{"id": "Q1", "stem": "Where does Nam live?", "answer": "He lives in Ha Noi.", "lines": 1}
```

### `heading_matching`
```json
{"id": "Q1", "stem": "Match the headings with the paragraphs.", "items": [{"left": "Paragraph 1", "right": "A. How to stay healthy"}], "answer": "1-A"}
```

### `reference_word`
```json
{"id": "Q1", "stem": "The word 'them' in paragraph 2 refers to ________.", "options": ["students", "books", "teachers", "schools"], "answer": "B"}
```

### `closest_opposite_meaning`
```json
{"id": "Q1", "stem": "The word 'modern' is OPPOSITE in meaning to ________.", "options": ["old", "new", "large", "clean"], "answer": "A"}
```

### `notice_reading`
Use a `notice_box` block before the question group.

```json
{"type": "notice_box", "text": "ALL VISITORS MUST REGISTER AT THE ENTRANCE."}
```

```json
{"id": "Q1", "stem": "What does the notice say?", "options": ["Visitors must sign in.", "Visitors can enter freely."], "answer": "A"}
```

### `sentence_ordering`
```json
{"id": "Q1", "stem": "Put the sentences in the correct order.", "items": ["a. Then we visited the museum.", "b. Last Sunday, our class went on a trip.", "c. Finally, we returned home."], "answer": "b-a-c"}
```

### `sentence_insertion`
```json
{"id": "Q1", "stem": "Choose the best sentence to fill in the blank.", "options": ["We learned many new things there.", "I do not like vegetables."], "answer": "A"}
```

## Listening

Listening tasks require top-level `listening.transcript`. MP3 generation remains optional until confirmed. Do not put the transcript in the student question area as a passage/text block or question passage. Dialogue transcripts must have one speaker turn per line.

### `listening_mcq`
```json
{"id": "Q1", "stem": "Where did Lan go last weekend?", "options": ["Ninh Thuan", "Sa Pa", "Ha Noi", "Da Nang"], "answer": "A"}
```

### `listening_tf`
```json
{"id": "Q1", "stem": "Nam likes making models.", "options": ["T", "F"], "answer": "T"}
```

### `listening_gap_fill`
```json
{"id": "Q1", "stem": "Mai's hobby is collecting ________.", "answer": "coins"}
```

### `listening_table_completion`
Use `resource_table` for table-shaped answer spaces.

```text
Name | Activity | Time
Mai  | ________ | 7:00
```

### `listening_matching`
```json
{"id": "Q1", "stem": "Match each speaker with the correct activity.", "items": ["Speaker 1", "Speaker 2", "A. playing football", "B. reading books"], "answer": "1-A, 2-B"}
```

## Writing

### `guided_sentence_writing`
```json
{"id": "Q1", "stem": "My brother / like / watch / cartoons / evening.", "answer": "My brother likes watching cartoons in the evening.", "lines": 1}
```

### `sentence_rewrite`
```json
{"id": "Q1", "stem": "My house is smaller than your house.", "prompt": "Your house _______________________________________________.", "answer": "Your house is bigger than my house.", "lines": 1}
```

### `rewrite_with_given_word`
```json
{"id": "Q1", "stem": "I like English more than Maths. (PREFER)", "given_word": "PREFER", "prompt": "I prefer ________________________________________________.", "answer": "I prefer English to Maths.", "lines": 1}
```

### `guided_paragraph`
```json
{
  "id": "Q1",
  "stem": "Write 60-80 words about your favourite TV programme. Include: its name, when you watch it, why you like it.",
  "answer": "Sample answer required in teacher version.",
  "lines": 6
}
```

### `email_writing`
```json
{
  "id": "Q1",
  "stem": "Write an email of 60-80 words to invite your friend to your birthday party. Include time, place, and activities.",
  "answer": "Sample email required in teacher version.",
  "lines": 8
}
```

### `picture_prompt_writing`
Use `picture_prompt` when image support is available; otherwise describe the picture in text.

### `word_form_writing`
```json
{"id": "Q1", "stem": "We should protect the ________ environment. (NATURE)", "answer": "natural"}
```

## Default Generation Rules

- For worksheet output, visible numbering should usually reset per exercise.
- For exam output, visible numbering should usually be `Question 1...N`.
- MCQ questions should use four options for exam papers unless the teacher asks otherwise.
- Worksheet MCQ can use three or four options depending on grade and difficulty.
- Writing tasks need lines in the student copy and a sample answer in the teacher copy.
- Speaking cards need prompts and rubrics; do not force a single fixed answer.
