# eng-test-gen

Bộ công cụ tạo đề kiểm tra, phiếu bài tập tiếng Anh THCS (lớp 6–9) theo chương trình **Global Success**.

## Tổng quan

```
eng-test-gen/
├── kb_extract.py           # Trích xuất từ giáo án .docx → SQLite knowledge base
├── knowledge_base.db       # Cơ sở dữ liệu từ vựng, ngữ pháp, cấu trúc bài
├── kb_mcp/                 # MCP server (stdio) — cung cấp tool cho Claude Code
├── skills/
│   ├── english-assessment-planner/   # Lên kế hoạch nội dung, xác nhận với giáo viên
│   └── english-assessment-producer/  # Sinh assessment.json → render DOCX
├── ref_data/               # Giáo án nguồn (GA TA 6–9) và file tham khảo
└── outputs/               # Đầu ra: plan, DOCX, JSON, audio
```

## Cài đặt nhanh (Linux)

```bash
# Cài trực tiếp từ GitHub
curl -fsSL https://github.com/Shaney17/eng-test-gen/raw/main/scripts/install_linux.sh | bash
```

Hoặc cài từ repo đã clone:

```bash
git clone https://github.com/Shaney17/eng-test-gen.git --depth=1 /tmp/eng-test-gen
bash /tmp/eng-test-gen/scripts/install_linux.sh
```

Script sẽ tự động:
1. Hỏi chọn agent cần cài skills ở lần cài đầu tiên; các lần chạy sau tự cập nhật lại các agent đã cài trước đó
2. Tải source từ GitHub nếu chạy bằng `curl | bash`
3. Cập nhật `knowledge_base.db` theo bản mới nhất trong source/DB URL
4. Copy/cập nhật app files vào `~/.local/share/english-assessment`
5. Cài `python3-venv` trên Ubuntu/Debian nếu máy đang thiếu
6. Tạo Python venv và cài `mcp`, `python-docx`, `requests`, `pyyaml`, `wordfreq`
7. Cài skills và cấu hình MCP server cho agent đã chọn

Mặc định DB được tải từ:

```text
https://raw.githubusercontent.com/Shaney17/eng-test-gen/main/knowledge_base.db
```

Các tùy chọn khác:

```bash
# Chỉ cài cho Claude Code
curl -fsSL https://github.com/Shaney17/eng-test-gen/raw/main/scripts/install_linux.sh | bash -s -- --yes --agents claude

# Cài không cần xác nhận, thư mục tùy chỉnh
curl -fsSL https://github.com/Shaney17/eng-test-gen/raw/main/scripts/install_linux.sh | bash -s -- --yes --install-dir /path/to/dir --agents all

# Non-interactive mode phải truyền rõ --agents
curl -fsSL https://github.com/Shaney17/eng-test-gen/raw/main/scripts/install_linux.sh | bash -s -- --yes --agents codex

# Sau khi đã cài ít nhất một lần, lệnh này tự update đúng các agent đã cài trước đó
curl -fsSL https://github.com/Shaney17/eng-test-gen/raw/main/scripts/install_linux.sh | bash -s -- --yes

# Cài từ branch/tag khác
curl -fsSL https://github.com/Shaney17/eng-test-gen/raw/main/scripts/install_linux.sh | bash -s -- --ref main

# Dùng DB URL riêng, ví dụ release asset
curl -fsSL https://github.com/Shaney17/eng-test-gen/raw/main/scripts/install_linux.sh | bash -s -- --db-url https://github.com/Shaney17/eng-test-gen/releases/latest/download/knowledge_base.db

# Bỏ qua bước cấu hình MCP (chỉ copy file)
curl -fsSL https://github.com/Shaney17/eng-test-gen/raw/main/scripts/install_linux.sh | bash -s -- --skip-mcp-config
```

## Kiến trúc hai bước

| Bước | Skill | Đầu vào | Đầu ra |
|---|---|---|---|
| 1. Lên kế hoạch | `english-assessment-planner` | Yêu cầu giáo viên (lớp, unit, loại tài liệu) | Blueprint xác nhận bởi giáo viên |
| 2. Sinh tài liệu | `english-assessment-producer` | Blueprint đã duyệt | `assessment.json` → `.docx` |

**Luôn dùng planner TRƯỚC producer cho mọi yêu cầu ban đầu.** Xem thêm phần **Sử dụng** bên dưới.

## Knowledge Base (SQLite)

```
units           — đơn vị bài học (grade, unit_number, title, topic)
lessons         — 7 bài học/unit (lesson_name, skill_focus)
vocabulary      — từ vựng (word, IPA, meaning_en, meaning_vi)
grammar_points  — ngữ pháp (point_name, form, examples)
questions       — ngân hàng câu hỏi (được sinh sau, theo dõi used_count)
matrices        — ma trận đề mẫu (cấu trúc test)
```

## MCP Server (`kb_mcp/server.py`)

Cung cấp các tool cho Claude Code qua giao thức stdio:

- `get_unit_info` — metadata + cấu trúc bài học của unit
- `get_vocab` — danh sách từ vựng (lọc theo lesson/skill)
- `get_grammar` — các mục ngữ pháp
- `list_questions` — truy vấn ngân hàng câu hỏi (ưu tiên câu chưa dùng)
- `add_questions` — thêm câu hỏi đã sinh vào ngân hàng
- `mark_used` — đánh dấu câu hỏi đã sử dụng
- `get_matrices` / `add_matrix` — quản lý ma trận đề
- `search_vocab` — tìm từ theo từ khóa

### Chạy MCP server

```bash
# Mặc định: stdio transport
python3 kb_mcp/server.py

# Hoặc với biến môi trường
ENGLISH_KB_DB_PATH=/path/to/db MCP_TRANSPORT=stdio python3 kb_mcp/server.py
```

## Trích xuất Knowledge Base (`kb_extract.py`)

```bash
# Trích xuất tất cả các lớp
python3 kb_extract.py

# Chỉ lớp 6
python3 kb_extract.py --grade 6

# Xem trước mà không chèn vào DB
python3 kb_extract.py --dry-run
```

Dữ liệu nguồn: các file `.docx` giáo án trong `ref_data/GA TA 6` … `GA TA 9`.

## Skills

### `english-assessment-planner`

1. Query KB theo lớp/unit
2. Đề xuất cấu trúc bài (phần, loại câu hỏi, số lượng, mức độ, điểm)
3. Trình cho giáo viên dạng **blueprint Markdown**
4. Chờ giáo viên xác nhận → chuyển sang producer

### `english-assessment-producer`

1. Sinh `assessment.json` từ blueprint đã duyệt
2. Validate JSON
3. Render thành `.docx` (đáp án đi kèm nếu requested)
4. Nếu có bài nghe: sinh transcript + audio manifest

## Các dạng bài được hỗ trợ

| Nhóm | Dạng bài |
|---|---|
| Phonetics | `pronunciation_odd_one`, `stress_odd_one` |
| Vocabulary | `vocab_mcq`, `word_bank_gap_fill`, `missing_letters`, `odd_one_topic`, `matching`, `word_form`, `crossword` |
| Grammar | `grammar_mcq`, `verb_form`, `grammar_gap_fill`, `choose_between_forms`, `error_correction` |
| Writing | `sentence_rewrite`, `rewrite_with_given_word`, `sentence_combining`, `sentence_building`, `guided_paragraph` |
| Reading | `reading_mcq`, `reading_gap_fill`, `reading_tf` |
| Listening | `listening_mcq`, `listening_gap_fill`, `listening_tf` |

## Quy ước quan trọng

- **Không** dùng `Yes/No` hay `meaning_matching` làm exercise format.
- Vocabulary MCQ phải là câu hỏi trong ngữ cảnh tiếng Anh, không phải EN→VI hay VI→EN.
- `reading_tf` = T/F/NG (điền chữ, không có A/B/C/D).
- `reading_gap_fill` mỗi chỗ trống có A/B/C/D riêng, không dùng word bank chung.
- `rewrite_with_given_word` phải ghi rõ từ gợi ý.
- Câu hỏi đặt (`question_making`) cần gạch chân phần gạch trong đề, từ căng âm thì không gạch chân.

## Output layout

```
outputs/<slug>/
├── plan.json
├── blueprint.md
├── assessment.json
├── <title>.docx
├── audio_manifest.json
└── audio/
    └── *.mp3
```

Quy ước: `skills/` chỉ chứa skill, scripts và references. Không lưu plan, JSON sinh đề, DOCX hoặc audio trong `skills/`; mọi file được tạo phải nằm trong `outputs/<slug>/`.
