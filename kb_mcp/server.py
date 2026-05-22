#!/usr/bin/env python3
"""
KB MCP Server — English Test Generator
Transport: stdio (Claude Code integration)

Tools:
  get_unit_info      — unit metadata + lesson structure
  get_vocab          — vocabulary list (grade+unit, optional lesson/skill filter)
  get_grammar        — grammar points (grade+unit)
  list_questions     — query question bank (unused-first, filterable)
  add_questions      — batch insert generated questions
  mark_used          — mark question IDs as used
  get_matrices       — list test matrix templates
  add_matrix         — create new matrix template
  search_vocab       — search vocab by keyword across all grades

Setup:
  pip install mcp
  Register in Claude Code: see README_MCP.md
"""

import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP

# ── Config ────────────────────────────────────────────────────────────────────

DB_PATH = Path(os.environ.get("ENGLISH_KB_DB_PATH", Path(__file__).parent.parent / "knowledge_base.db"))
MCP_HOST = os.environ.get("MCP_HOST", "127.0.0.1")
MCP_PORT = int(os.environ.get("MCP_PORT", "8765"))
MCP_TRANSPORT = os.environ.get("MCP_TRANSPORT", "stdio")

mcp = FastMCP(
    name="english-kb",
    host=MCP_HOST,
    port=MCP_PORT,
    instructions=(
        "Knowledge base for Global Success THCS English curriculum. "
        "Contains vocabulary (IPA + Vietnamese), grammar points, question bank, "
        "and test matrix templates for grades 6-9. "
        "Always query this KB before generating exercises — use actual KB data "
        "rather than making up vocabulary or grammar rules."
    ),
)

# ── DB Helpers ────────────────────────────────────────────────────────────────

def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = DELETE")  # virtiofs-safe
    return conn


def _row_to_dict(row: sqlite3.Row) -> dict:
    return dict(row)


def _rows_to_list(rows) -> list[dict]:
    return [dict(r) for r in rows]

# ── Tools ─────────────────────────────────────────────────────────────────────

@mcp.tool()
def get_unit_info(grade: int, unit_number: int) -> str:
    """
    Get metadata and lesson structure for a specific grade+unit.

    Returns: unit title, topic, list of lessons (name + skill_focus).
    Use this first to understand what a unit covers before generating exercises.

    Args:
        grade: Grade level (6, 7, 8, or 9)
        unit_number: Unit number (1-12)
    """
    conn = get_db()
    try:
        unit = conn.execute(
            "SELECT * FROM units WHERE grade=? AND unit_number=?",
            (grade, unit_number)
        ).fetchone()

        if not unit:
            return json.dumps({"error": f"Unit not found: Grade {grade} Unit {unit_number}"})

        unit_dict = _row_to_dict(unit)
        lessons = _rows_to_list(conn.execute(
            "SELECT lesson_number, lesson_name, skill_focus "
            "FROM lessons WHERE unit_id=? ORDER BY lesson_number",
            (unit_dict["id"],)
        ).fetchall())

        # Counts
        vocab_count = conn.execute(
            "SELECT COUNT(*) FROM vocabulary WHERE unit_id=?",
            (unit_dict["id"],)
        ).fetchone()[0]
        grammar_count = conn.execute(
            "SELECT COUNT(*) FROM grammar_points WHERE unit_id=?",
            (unit_dict["id"],)
        ).fetchone()[0]
        question_count = conn.execute(
            "SELECT COUNT(*) FROM questions WHERE unit_id=?",
            (unit_dict["id"],)
        ).fetchone()[0]

        result = {
            "grade": grade,
            "unit_number": unit_number,
            "title": unit_dict["title"],
            "topic": unit_dict["topic"],
            "lessons": lessons,
            "stats": {
                "vocab_items": vocab_count,
                "grammar_points": grammar_count,
                "questions_in_bank": question_count,
            }
        }
        return json.dumps(result, ensure_ascii=False, indent=2)
    finally:
        conn.close()


@mcp.tool()
def get_vocab(
    grade: int,
    unit_number: int,
    lesson_number: Optional[int] = None,
    skill: Optional[str] = None,
) -> str:
    """
    Get vocabulary list for a grade+unit, optionally filtered by lesson.

    Each vocab item includes: word, part_of_speech, pronunciation_ipa,
    meaning_en, meaning_vi.

    Args:
        grade: Grade level (6, 7, 8, or 9)
        unit_number: Unit number (1-12)
        lesson_number: Optional — filter by specific lesson (1-7)
        skill: Optional — filter lessons by skill focus
                         (vocabulary, grammar, reading, listening, speaking, writing)
    """
    conn = get_db()
    try:
        unit = conn.execute(
            "SELECT id FROM units WHERE grade=? AND unit_number=?",
            (grade, unit_number)
        ).fetchone()

        if not unit:
            return json.dumps({"error": f"Unit not found: Grade {grade} Unit {unit_number}"})

        unit_id = unit["id"]
        query = """
            SELECT v.word, v.part_of_speech, v.pronunciation_ipa,
                   v.meaning_en, v.meaning_vi,
                   l.lesson_number, l.lesson_name, l.skill_focus
            FROM vocabulary v
            LEFT JOIN lessons l ON v.lesson_id = l.id
            WHERE v.unit_id = ?
        """
        params: list = [unit_id]

        if lesson_number is not None:
            query += " AND l.lesson_number = ?"
            params.append(lesson_number)

        if skill:
            query += " AND l.skill_focus LIKE ?"
            params.append(f"%{skill}%")

        query += " ORDER BY l.lesson_number, v.id"
        rows = _rows_to_list(conn.execute(query, params).fetchall())

        return json.dumps({
            "grade": grade,
            "unit_number": unit_number,
            "total": len(rows),
            "vocabulary": rows,
        }, ensure_ascii=False, indent=2)
    finally:
        conn.close()


@mcp.tool()
def get_grammar(grade: int, unit_number: int) -> str:
    """
    Get grammar points for a grade+unit.

    Each grammar point includes: point_name, form_description (the grammar rule/form),
    examples (list of example sentences).

    Args:
        grade: Grade level (6, 7, 8, or 9)
        unit_number: Unit number (1-12)
    """
    conn = get_db()
    try:
        unit = conn.execute(
            "SELECT id FROM units WHERE grade=? AND unit_number=?",
            (grade, unit_number)
        ).fetchone()

        if not unit:
            return json.dumps({"error": f"Unit not found: Grade {grade} Unit {unit_number}"})

        unit_id = unit["id"]
        rows = conn.execute(
            """SELECT g.point_name, g.form_description, g.examples,
                      l.lesson_number, l.lesson_name
               FROM grammar_points g
               LEFT JOIN lessons l ON g.lesson_id = l.id
               WHERE g.unit_id = ?
               ORDER BY l.lesson_number, g.id""",
            (unit_id,)
        ).fetchall()

        grammar = []
        for r in rows:
            item = dict(r)
            item["examples"] = json.loads(item["examples"]) if item["examples"] else []
            grammar.append(item)

        return json.dumps({
            "grade": grade,
            "unit_number": unit_number,
            "total": len(grammar),
            "grammar_points": grammar,
        }, ensure_ascii=False, indent=2)
    finally:
        conn.close()


@mcp.tool()
def list_questions(
    grade: int,
    unit_number: int,
    knowledge_type: Optional[str] = None,
    exercise_type: Optional[str] = None,
    difficulty: Optional[int] = None,
    limit: int = 20,
    unused_first: bool = True,
) -> str:
    """
    List questions from the question bank for a grade+unit.

    Questions are sorted by used_count ascending (unused first) by default,
    so repeated calls naturally pick fresh questions.

    Args:
        grade: Grade level (6, 7, 8, or 9)
        unit_number: Unit number (1-12)
        knowledge_type: Filter by knowledge area:
                        'vocabulary' | 'grammar' | 'reading' | 'listening'
        exercise_type: Filter by exercise format:
                       'MCQ' | 'TF' | 'fill_blank' | 'matching' |
                       'ordering' | 'writing' | 'translation'
        difficulty: Filter by difficulty (1=easy, 2=medium, 3=hard)
        limit: Max questions to return (default 20)
        unused_first: Sort by used_count ascending (default True)
    """
    conn = get_db()
    try:
        unit = conn.execute(
            "SELECT id FROM units WHERE grade=? AND unit_number=?",
            (grade, unit_number)
        ).fetchone()

        if not unit:
            return json.dumps({"error": f"Unit not found: Grade {grade} Unit {unit_number}"})

        unit_id = unit["id"]
        query = """
            SELECT q.id, q.knowledge_type, q.exercise_type, q.difficulty,
                   q.content, q.answer, q.used_count, q.last_used_date,
                   l.lesson_number, l.lesson_name
            FROM questions q
            LEFT JOIN lessons l ON q.lesson_id = l.id
            WHERE q.unit_id = ?
        """
        params: list = [unit_id]

        if knowledge_type:
            query += " AND q.knowledge_type = ?"
            params.append(knowledge_type)
        if exercise_type:
            query += " AND q.exercise_type = ?"
            params.append(exercise_type)
        if difficulty is not None:
            query += " AND q.difficulty = ?"
            params.append(difficulty)

        order = "q.used_count ASC, q.id ASC" if unused_first else "q.id ASC"
        query += f" ORDER BY {order} LIMIT ?"
        params.append(limit)

        rows = conn.execute(query, params).fetchall()
        questions = []
        for r in rows:
            item = dict(r)
            item["content"] = json.loads(item["content"]) if item["content"] else {}
            item["answer"] = json.loads(item["answer"]) if item["answer"] else {}
            questions.append(item)

        total_in_bank = conn.execute(
            "SELECT COUNT(*) FROM questions WHERE unit_id=?", (unit_id,)
        ).fetchone()[0]

        return json.dumps({
            "grade": grade,
            "unit_number": unit_number,
            "total_in_bank": total_in_bank,
            "returned": len(questions),
            "questions": questions,
        }, ensure_ascii=False, indent=2)
    finally:
        conn.close()


@mcp.tool()
def add_questions(questions: list[dict]) -> str:
    """
    Add generated questions to the question bank.

    Call this after generating exercises so they can be reused later
    and tracked to avoid repetition.

    Each question dict must have:
      - unit_id (int): from get_unit_info
      - knowledge_type (str): 'vocabulary' | 'grammar' | 'reading' | 'listening'
      - exercise_type (str): 'MCQ' | 'TF' | 'fill_blank' | 'matching' |
                             'ordering' | 'writing' | 'translation'
      - difficulty (int): 1=easy, 2=medium, 3=hard
      - content (dict): question content (stem, options, passage, etc.)
      - answer (dict): correct answer(s)
    Optional:
      - lesson_id (int): specific lesson

    Args:
        questions: List of question dicts as described above

    Returns:
        Count of inserted questions and their new IDs.
    """
    conn = get_db()
    inserted_ids = []
    try:
        for q in questions:
            cur = conn.execute(
                """INSERT INTO questions
                   (unit_id, lesson_id, knowledge_type, exercise_type,
                    difficulty, content, answer)
                   VALUES (?,?,?,?,?,?,?)""",
                (
                    q["unit_id"],
                    q.get("lesson_id"),
                    q["knowledge_type"],
                    q["exercise_type"],
                    q.get("difficulty", 1),
                    json.dumps(q.get("content", {}), ensure_ascii=False),
                    json.dumps(q.get("answer", {}), ensure_ascii=False),
                )
            )
            inserted_ids.append(cur.lastrowid)
        conn.commit()
        return json.dumps({
            "inserted": len(inserted_ids),
            "ids": inserted_ids,
        })
    except Exception as e:
        conn.rollback()
        return json.dumps({"error": str(e)})
    finally:
        conn.close()


@mcp.tool()
def mark_used(question_ids: list[int]) -> str:
    """
    Mark questions as used after including them in a worksheet or test.

    Increments used_count and sets last_used_date for each question ID.
    Call this after finalizing a worksheet/test to track which questions
    have been given to students.

    Args:
        question_ids: List of question IDs to mark as used
    """
    conn = get_db()
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        conn.executemany(
            """UPDATE questions
               SET used_count = used_count + 1, last_used_date = ?
               WHERE id = ?""",
            [(today, qid) for qid in question_ids]
        )
        conn.commit()
        return json.dumps({
            "marked_used": len(question_ids),
            "date": today,
        })
    finally:
        conn.close()


@mcp.tool()
def get_matrices(grade: Optional[int] = None) -> str:
    """
    List test matrix templates, optionally filtered by grade.

    A matrix defines the structure of a test: how many questions per section,
    what knowledge type, exercise type, and difficulty level for each section.

    Args:
        grade: Optional grade filter (6, 7, 8, or 9). None = all grades.
    """
    conn = get_db()
    try:
        if grade is not None:
            rows = conn.execute(
                "SELECT * FROM matrices WHERE grade=? OR grade IS NULL ORDER BY id",
                (grade,)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM matrices ORDER BY id").fetchall()

        matrices = []
        for r in rows:
            item = dict(r)
            item["structure"] = json.loads(item["structure"])
            matrices.append(item)

        return json.dumps({
            "total": len(matrices),
            "matrices": matrices,
        }, ensure_ascii=False, indent=2)
    finally:
        conn.close()


@mcp.tool()
def add_matrix(
    name: str,
    description: str,
    structure: list[dict],
    grade: Optional[int] = None,
) -> str:
    """
    Create a new test matrix template.

    Args:
        name: Matrix name (e.g. "15-minute vocab quiz", "45-minute unit test")
        description: What this matrix is for
        structure: List of section dicts. Each section has:
            - section (str): section name, e.g. "Vocabulary"
            - knowledge_type (str): 'vocabulary' | 'grammar' | 'reading' | 'listening'
            - exercise_type (str): 'MCQ' | 'TF' | 'fill_blank' | 'matching' |
                                   'ordering' | 'writing'
            - count (int): number of questions
            - difficulty (int): 1=easy, 2=medium, 3=hard
            - points_each (float): optional points per question
        grade: Optional — if this matrix applies to a specific grade only

    Example structure:
        [
          {"section": "Vocabulary", "knowledge_type": "vocabulary",
           "exercise_type": "MCQ", "count": 5, "difficulty": 1, "points_each": 0.2},
          {"section": "Grammar",   "knowledge_type": "grammar",
           "exercise_type": "fill_blank", "count": 5, "difficulty": 2, "points_each": 0.2},
          {"section": "Reading",   "knowledge_type": "reading",
           "exercise_type": "TF", "count": 5, "difficulty": 2, "points_each": 0.2}
        ]
    """
    conn = get_db()
    try:
        cur = conn.execute(
            "INSERT INTO matrices (name, grade, description, structure) VALUES (?,?,?,?)",
            (name, grade, description, json.dumps(structure, ensure_ascii=False))
        )
        conn.commit()
        return json.dumps({
            "created": True,
            "id": cur.lastrowid,
            "name": name,
            "total_questions": sum(s.get("count", 0) for s in structure),
        })
    finally:
        conn.close()


@mcp.tool()
def search_vocab(keyword: str, grade: Optional[int] = None) -> str:
    """
    Search vocabulary across all units by keyword (English word or Vietnamese meaning).

    Useful for checking if a word is already in the KB before generating exercises.

    Args:
        keyword: Search term (partial match on word or meaning_vi)
        grade: Optional grade filter
    """
    conn = get_db()
    try:
        like = f"%{keyword}%"
        if grade is not None:
            rows = conn.execute(
                """SELECT v.word, v.pronunciation_ipa, v.meaning_vi,
                          u.grade, u.unit_number, u.title
                   FROM vocabulary v JOIN units u ON v.unit_id=u.id
                   WHERE u.grade=? AND (v.word LIKE ? OR v.meaning_vi LIKE ?)
                   ORDER BY u.unit_number, v.word
                   LIMIT 50""",
                (grade, like, like)
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT v.word, v.pronunciation_ipa, v.meaning_vi,
                          u.grade, u.unit_number, u.title
                   FROM vocabulary v JOIN units u ON v.unit_id=u.id
                   WHERE v.word LIKE ? OR v.meaning_vi LIKE ?
                   ORDER BY u.grade, u.unit_number, v.word
                   LIMIT 50""",
                (like, like)
            ).fetchall()

        return json.dumps({
            "keyword": keyword,
            "results": _rows_to_list(rows),
        }, ensure_ascii=False, indent=2)
    finally:
        conn.close()


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"KB database not found at {DB_PATH}\n"
            "Run: python3 kb_extract.py  to build it first."
        )
    mcp.run(transport=MCP_TRANSPORT)
