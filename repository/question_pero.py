import sqlite3
from quiz_app.database.connection import get_connection, fetchone, fetchall
from quiz_app.logger import logger

def fetch_random_question(level):

    return fetchone("""
    SELECT id,
    question_title,
    difficulty
    FROM questions
    WHERE difficulty = ?
    ORDER BY RANDOM()
    LIMIT 1""", (level,))

def fetch_answers(question_id):
    return fetchall("""
    SELECT id,
    answer_title,
    is_correct
    FROM answer_variants
    WHERE question_id = ?""", (question_id,))

def fetch_translated_question(question_id, lang):

    return fetchone("""
    SELECT translated_title
    FROM translated_questions
    WHERE question_id = ?
    AND language = ?""", (question_id, lang))

def fetch_translated_answers(answers_id, language):

    return fetchall("""
    SELECT translated_title
    FROM translated_answers
    WHERE answer_id IN (?, ?, ?, ?)
    AND language = ?""", (*answers_id, language))

def fetch_answer_correctness(answer_id):

    return fetchone("""
    SELECT is_correct
    FROM answer_variants
    WHERE id = ?""", (answer_id,))

def fetch_answer_by_id(answer_id):

    return fetchone("""
    SELECT answer_title
    FROM answer_variants
    WHERE id = ?""", (answer_id,))

def fetch_translated_answer_by_id(answer_id, lang):

    return fetchone("""
    SELECT translated_title
    FROM translated_answers
    WHERE answer_id = ?
    AND language = ?""", (answer_id, lang))

def fetch_answers_id(question_id):

    return fetchall("""
    SELECT id
    FROM answer_variants
    WHERE question_id = ?
    ORDER BY id""", (question_id,))

def fetch_correct_answer(question_id):

    return fetchone("""
    SELECT id,
    answer_title
    FROM answer_variants
    WHERE question_id = ?
    AND is_correct = 1""", (question_id,))


# For import questions to the database

def insert_question_transaction(question_title, category, difficulty, answers):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO questions (question_title, category, difficulty)
            VALUES (?, ?, ?)""", (question_title, category, difficulty))

        question_id = cur.lastrowid

        for answer, is_correct in answers:
            cur.execute("""
            INSERT INTO answer_variants (question_id, answer_title, is_correct)
            VALUES (?, ?, ?)""", (question_id, answer, is_correct))

        conn.commit()
    except sqlite3.Error:
        logger.error(f"Failed to load question")
        conn.rollback()
    finally:
        conn.close()

def insert_translated_questions(question_id, lang, translated_question, translated_answers):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO translated_questions (question_id, language, translated_title)
            VALUES (?, ?, ?)""", (question_id, lang, translated_question))

        for answer_id, title in translated_answers:
            cur.execute("""
                INSERT INTO translated_answers (answer_id, language, translated_title)
                VALUES (?, ?, ?)""", (answer_id, lang, title))

        conn.commit()
    except sqlite3.Error:
        logger.error(f"Failed to load translated_question {question_id}")
        conn.rollback()
    finally:
        conn.close()

def fetch_questions(offset):

    return fetchall("""
    SELECT id,
    question_title
    FROM questions
    LIMIT 100
    OFFSET ?""", (offset,))