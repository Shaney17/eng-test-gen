# Common English Exercise Formats In Vietnamese Secondary Schools

Use these formats when planning worksheets, quizzes, and tests. This is a closed internal taxonomy, but teacher-facing plans should use short natural descriptions instead of raw codes.

Teacher-facing rule:

- In the visible blueprint table, write `Exercise format` as a short description, not a code.
- Keep raw codes internal; do not print a technical transfer section in the teacher-facing plan.

Example:

```text
Visible to teacher: MCQ từ vựng trong ngữ cảnh tiếng Anh
Internal code: vocab_mcq
```

Forbidden labels:

- `Yes/No`, `yes_no`, `yes-no`: use `reading_tf`, `listening_tf`, or `short_answer` instead.
- `meaning_matching`, `meaning matching`: not allowed. Use English-context `vocab_mcq` instead.
- `true_false`: use `reading_tf` or `listening_tf`.
- `fill_blank`: use `word_bank_gap_fill`, `grammar_gap_fill`, `reading_gap_fill`, or `listening_gap_fill`.

Teacher-facing restriction:

- Do not put "Yes/No" in the `Exercise format` column.
- If the lesson grammar is yes/no question formation, write the exercise format as `MCQ ngữ pháp` or `Đặt câu hỏi theo gợi ý`.
- Put the grammar content separately as `Grammar focus: Yes/No questions`.

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

## Teacher-Facing Names

| Producer code | Teacher-facing wording |
|---|---|
| `pronunciation_odd_one` | Chọn từ có phần gạch chân phát âm khác |
| `stress_odd_one` | Chọn từ có trọng âm khác |
| `vocab_mcq` | MCQ từ vựng trong ngữ cảnh tiếng Anh |
| `matching` | Nối cặp thông tin theo yêu cầu |
| `word_bank_gap_fill` | Điền từ vào câu/đoạn với word bank |
| `missing_letters` | Hoàn thành chữ cái còn thiếu |
| `word_form` | Cho dạng đúng của từ trong ngoặc |
| `odd_one_topic` | Chọn từ khác nhóm |
| `label_picture` | Nhìn tranh và viết từ/cụm từ |
| `crossword` | Ô chữ theo gợi ý |
| `grammar_mcq` | MCQ ngữ pháp |
| `verb_form` | Chia dạng đúng của động từ |
| `grammar_gap_fill` | Điền cấu trúc/ngữ pháp phù hợp |
| `choose_between_forms` | Chọn một trong hai dạng cho sẵn |
| `error_correction` | Tìm và sửa lỗi sai |
| `sentence_rewrite` | Viết lại câu sao cho nghĩa không đổi |
| `rewrite_with_given_word` | Viết lại câu dùng từ cho sẵn |
| `sentence_combining` | Nối câu dùng từ/cấu trúc cho sẵn |
| `sentence_building` | Dùng từ gợi ý viết thành câu hoàn chỉnh |
| `question_making` | Đặt câu hỏi theo gợi ý/phần gạch chân |
| `dialogue_completion` | Chọn câu đáp phù hợp trong hội thoại |
| `dialogue_ordering` | Sắp xếp hội thoại |
| `speaking_card` | Thẻ nói theo chủ đề/gợi ý |
| `reading_mcq` | Đọc hiểu và trả lời câu hỏi MCQ |
| `reading_tf` | Đọc đoạn văn và điền T/F/NG |
| `reading_gap_fill` | Điền từ vào đoạn đọc |
| `short_answer` | Đọc và trả lời ngắn |
| `heading_matching` | Nối tiêu đề với đoạn văn |
| `reference_word` | Xác định từ quy chiếu trong bài đọc |
| `closest_opposite_meaning` | Chọn từ đồng nghĩa/trái nghĩa theo ngữ cảnh |
| `notice_reading` | Đọc biển báo/thông báo và chọn đáp án |
| `sentence_ordering` | Sắp xếp câu thành đoạn logic |
| `sentence_insertion` | Chọn câu phù hợp điền vào đoạn |
| `listening_mcq` | Nghe và chọn đáp án đúng |
| `listening_tf` | Nghe và điền T/F/NG |
| `listening_gap_fill` | Nghe và điền thông tin còn thiếu |
| `listening_table_completion` | Nghe và hoàn thành bảng |
| `listening_matching` | Nghe và nối thông tin |
| `guided_sentence_writing` | Viết câu hoàn chỉnh theo gợi ý |
| `guided_paragraph` | Viết đoạn văn ngắn theo gợi ý |
| `email_writing` | Viết email/tin nhắn theo yêu cầu |
| `picture_prompt_writing` | Viết theo tranh/gợi ý hình ảnh |
| `word_form_writing` | Cho dạng đúng của từ trong phần viết |

## Pronunciation / Phonetics

### `pronunciation_odd_one`
Instruction: `Choose the word whose underlined part is pronounced differently from the others.`

```text
Question 1. A. c<u>i</u>ty    B. b<u>i</u>cycle    C. r<u>i</u>ce    D. v<u>i</u>llage
```

Answer: one option letter.

Internal generation note: mark underlined sounds as `__i__` inside each option. Do not put the section instruction or target sound (`ee`, `ch`, `/i:/`, etc.) in each question. Each item should show only the number and options. Each option must be one real English word from the KB vocabulary only, not a phrase; use `dance`, not `folk dance`, and never invent pseudo-words. The underlined letters must be identical across all options, for example all four options underline `ch`.

### `stress_odd_one`
Instruction: `Choose the word that has a different stress pattern from the others.`

```text
Question 1. A. historic    B. exciting    C. expensive    D. beautiful
```

Answer: one option letter.

Do not underline letters in stress questions. Each option must be one real English word from the KB vocabulary only, not a phrase or invented pseudo-word.

## Vocabulary

### `vocab_mcq`
Instruction: `Choose the best answer to complete each sentence.`

```text
Question 1. Tet is a time for family ________.
A. gatherings    B. maps    C. buildings    D. robots
```

### `matching`
Instruction: `Match the words with their meanings.`

```text
A. decorate        1. a good or useful effect
B. benefit         2. make something look more attractive
C. responsibility  3. a duty to take care of something
```

Use this only when the teacher or blueprint explicitly asks for matching. Do not use meaning-translation matching.

### `word_bank_gap_fill`
Instruction: `Complete the sentences with the words from the box.`

Planning note: the word bank is a single resource box/table placed immediately before the questions, not after them and not repeated per item.

```text
Words: decorate | benefit | outdoor | patient
1. We often ________ our house before Tet.
2. Gardening is an ________ activity.
```

### `missing_letters`
Instruction: `Complete the words with missing letters.`

```text
1. I will catch the t_ _ _ _ from Ha Noi to Ho Chi Minh City.
2. You should avoid t_ _ _ _ _ _ jams.
```

### `word_form`
Instruction: `Give the correct form of the word in brackets.`

```text
Question 1. My sister is very ________ when she waits for the bus. (PATIENCE)
```

### `odd_one_topic`
Instruction: `Choose the odd one out.`

Planning note: use one shared instruction for the whole exercise. Do not plan or generate the same instruction again inside each question.

```text
Question 1. A. train    B. bus    C. plane    D. kitchen
```

### `label_picture`
Instruction: `Look at the pictures and write the correct words.`

```text
Picture 1: __________
Picture 2: __________
```

### `crossword`
Instruction: `Complete the sentences and do the crossword.`

```text
1. A fast train: b_ _ _ _ _ train
2. A vehicle that can fly: f_ _ _ _ _ car
```

Use a `crossword` block plus a `question_group` for clues.

## Grammar

### `grammar_mcq`
Instruction: `Choose the best answer to complete each sentence.`

```text
Question 1. You ________ make noise in the library.
A. should    B. shouldn't    C. can    D. are
```

### `verb_form`
Instruction: `Give the correct form of the verbs in brackets.`

```text
Question 1. My father ________ TV every evening. (watch)
```

### `grammar_gap_fill`
Instruction: `Complete the sentences with suitable grammar items.`

```text
Question 1. There is ________ orange on the table.
Question 2. We don't have ________ milk left.
```

### `choose_between_forms`
Instruction: `Choose the correct form.`

```text
Question 1. I think people will use / are using flying cars in the future.
```

### `error_correction`
Instruction: `Find one mistake in each sentence and correct it.`

```text
Question 1. She go to school by bus every day.
Mistake: ________  Correction: ________
```

### `sentence_rewrite`
Instruction: `Rewrite the sentence so that it has the same meaning as the first one.`

```text
Question 1. The new phone is cheaper than the old phone.
=> The old phone is __________________________________________.
```

### `rewrite_with_given_word`
Instruction: `Rewrite the sentence using the given word. Do not change the given word.`

```text
Question 1. The weather today is not as hot as yesterday. (THAN)
=> Yesterday ________________________________________________.
```

Each question must include the cue word, either after the original sentence or as a separate `given_word`/`cue_word` field.
Each question should also include a student answer prompt, usually with the first 1-2 words of the rewritten sentence.

### `sentence_combining`
Instruction: `Combine the sentences using the word given.`

```text
Question 1. I was tired. I finished my homework. (ALTHOUGH)
=> __________________________________________________________.
```

### `sentence_building`
Instruction: `Write complete sentences from the words and phrases given.`

```text
Question 1. We / visit / grandparents / next Sunday.
=> __________________________________________________________.
```

### `question_making`
Instruction: `Make questions for the underlined parts.`

```text
Question 1. Nam goes to school <u>by bike</u>.
=> __________________________________________________________?
```

Internal generation note: mark the underlined part as `__by bike__` in the stem.

## Communication / Speaking Support

### `dialogue_completion`
Instruction: `Choose the best response to complete the conversation.`

```text
Question 1.
Tourist: Could you tell me the way to the museum?
Local: ________
A. Go straight, then turn left.    B. I am fine.
C. No, I don't.                    D. It is mine.
```

### `dialogue_ordering`
Instruction: `Put the dialogue lines in the correct order.`

```text
a. Yes, I do. I like cartoons.
b. What is your favourite programme?
c. Do you like watching TV?
Answer: ________
```

### `speaking_card`
Instruction: `Use the prompts to talk with your partner.`

```text
Topic: Your neighbourhood
- Where do you live?
- What places are near your house?
- What do you like about it?
```

Speaking cards usually need a rubric, not a fixed answer key.

## Reading

### `reading_mcq`
Instruction: `Read the passage and choose the best answer to each question.`

Use this only for reading comprehension questions after a passage. The question stem must be a comprehension question, not a sentence with a blank.

```text
Question 1. What is the passage mainly about?
A. A school trip    B. A new robot    C. A TV programme    D. A festival
```

### `reading_tf`
Instruction: `Read the passage and write T (True), F (False), or NG (Not Given).`

```text
1. Mai visited her grandparents last weekend. ________
2. The village is near the sea. ________
```

This format has no A/B/C options. Students write T, F, or NG in the blank.

### `reading_gap_fill`
Instruction: `Choose the best option to complete the passage.`

Use this for cloze reading: the passage/sentence has numbered blanks and students choose the word/phrase that fits each blank. Do not use this for comprehension questions.
Do not add a word bank; each blank has its own A/B/C/D options. Render each item on one line: question number plus options, like phonetics.

```text
Tet is the most important festival in Viet Nam. People often (1) ________ their houses.
1. A. decorate    B. visit    C. watch    D. play
```

### `short_answer`
Instruction: `Read the passage and answer the questions.`

```text
Question 1. Where does Nam live?
Answer: _____________________________________________________.
```

### `heading_matching`
Instruction: `Match the headings with the paragraphs.`

```text
Headings:
A. How to stay healthy
B. A popular hobby
Paragraph 1: ...
Answer: 1. ________
```

### `reference_word`
Instruction: `Choose what the underlined word refers to.`

```text
Question 1. The word "them" in paragraph 2 refers to ________.
A. students    B. books    C. teachers    D. schools
```

### `closest_opposite_meaning`
Instruction: `Choose the word CLOSEST/OPPOSITE in meaning to the underlined word.`

```text
Question 1. The word "modern" is OPPOSITE in meaning to ________.
A. old    B. new    C. large    D. clean
```

### `notice_reading`
Instruction: `Read the notice/sign/announcement and choose the correct answer.`

```text
NOTICE: ALL VISITORS MUST REGISTER AT THE ENTRANCE.
Question 1. What does the notice say?
A. Visitors must sign in.    B. Visitors can enter freely.
```

### `sentence_ordering`
Instruction: `Put the sentences in the correct order to make a logical text.`

```text
a. Then we visited the museum.
b. Last Sunday, our class went on a trip.
c. Finally, we returned home.
Answer: ________
```

### `sentence_insertion`
Instruction: `Choose the best sentence to fill in the blank.`

```text
The trip was long, but we were excited. ________
A. We learned many new things there.
B. I do not like vegetables.
```

## Listening

### `listening_mcq`
Instruction: `Listen and choose the correct answer.`

```text
Question 1. Where did Lan go last weekend?
A. Ninh Thuan    B. Sa Pa    C. Ha Noi    D. Da Nang
```

### `listening_tf`
Instruction: `Listen and write T (True) or F (False).`

```text
1. Nam likes making models. ________
2. Mai went to the park yesterday. ________
```

### `listening_gap_fill`
Instruction: `Listen and complete the sentences.`

```text
Question 1. Mai's hobby is collecting ________.
```

### `listening_table_completion`
Instruction: `Listen and complete the table.`

```text
Name | Activity | Time
Mai  | ________ | 7:00
```

### `listening_matching`
Instruction: `Listen and match each speaker with the correct activity.`

```text
Speaker 1: ________
Speaker 2: ________
A. playing football    B. reading books
```

Listening formats require `listening.transcript`; MP3 is optional until confirmed. The transcript belongs in the answer key/transcript section only, not in the student question area. Dialogue transcripts must have one speaker turn per line.

## Writing

### `guided_sentence_writing`
Instruction: `Write complete sentences from the words and phrases given.`

```text
Question 1. My brother / like / watch / cartoons / evening.
=> __________________________________________________________.
```

### `sentence_rewrite`
Instruction: `Complete the second sentence so that it means the same as the first.`

```text
Question 1. My house is smaller than your house.
=> Your house _______________________________________________.
```

### `rewrite_with_given_word`
Instruction: `Rewrite the sentence using the given word. Do not change the given word.`

```text
Question 1. I like English more than Maths. (PREFER)
=> __________________________________________________________.
```

Each question must include the cue word, either after the original sentence or as a separate `given_word`/`cue_word` field.
Each question should also include a student answer prompt, usually with the first 1-2 words of the rewritten sentence.

### `guided_paragraph`
Instruction: `Write a paragraph using the prompts.`

```text
Write 60-80 words about your favourite TV programme.
You should write about:
- its name
- when you watch it
- why you like it
```

### `email_writing`
Instruction: `Write an email/message using the cues.`

```text
Write an email of 60-80 words to invite your friend to your birthday party.
Include: time, place, activities.
```

### `picture_prompt_writing`
Instruction: `Look at the picture(s) and write sentences/a paragraph.`

```text
Look at the pictures of Tet activities. Write 5 sentences about what people are doing.
```

### `word_form_writing`
Instruction: `Give the correct form of the word in brackets.`

```text
Question 1. We should protect the ________ environment. (NATURE)
```

## Default Planning Choices

- Worksheet: prefer `vocab_mcq`, `word_bank_gap_fill`, `missing_letters`, `grammar_gap_fill`, `sentence_building`, `sentence_rewrite`, and reading short-answer/gap-fill.
- 15-minute quiz: prefer `pronunciation_odd_one`, `vocab_mcq`, `grammar_mcq`, `verb_form`, short `reading_mcq`.
- Midterm/final test: prefer exam-style `global` numbering, mostly MCQ for language/reading/listening, with a short writing section if required.
- Speaking tasks: include cards and rubrics; do not force a single answer key.
