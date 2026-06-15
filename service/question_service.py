from deep_translator import GoogleTranslator
from quiz_app.game_rules import check_answer, questions_difficulty
from quiz_app.repository.question_pero import (fetch_answer_by_id, fetch_translated_question,
                                               fetch_translated_answers, fetch_translated_answer_by_id,
                                               fetch_questions, fetch_answers, fetch_answers_id,
                                               fetch_random_question, insert_question_transaction,
                                               insert_translated_questions, fetch_answer_correctness,
                                               fetch_correct_answer)

def get_correct_answer(question_id, variants, lang):
    correct = fetch_correct_answer(question_id)[0]

    correct_variant = ""
    for k, v in variants.items():
        if v == correct:
            if lang == "en":
                title = fetch_answer_by_id(v)[0]
            else:
                title = fetch_translated_answer_by_id(v, lang)[0]

            correct_variant = f"{k}) {title}"

    return correct_variant

def translate(text, target_lang):
    translated = GoogleTranslator(
        source="en",
        target=target_lang
    ).translate(text)

    return translated

def get_questions_with_limit(offset):
    return fetch_questions(offset)

def get_answers(question_id):
    return fetch_answers(question_id)

def get_answer_by_id(answer_id):
    answer = fetch_answer_by_id(answer_id)[0]
    return answer

def get_answers_id(question_id):
    answers = fetch_answers_id(question_id)
    return answers

def check_answer_correctness(answer_id):
    data = fetch_answer_correctness(answer_id)[0]
    return check_answer(data)

def get_difficulty(question_level):
    return questions_difficulty(question_level)

def get_question_and_answers(question_count):
    difficulty = get_difficulty(question_count)
    question = fetch_random_question(difficulty)
    question_id = question[0]
    question_title = question[1]

    answers = fetch_answers(question_id)

    return question_id, question_title, answers

def get_translated_question_and_answers(question_count, lang):
    difficulty = get_difficulty(question_count)
    question = fetch_random_question(difficulty)
    question_id = question[0]

    answers = get_answers(question_id)
    answer_ids = ()

    for answer in answers:
        answer_ids += (answer[0],)

    translated_quest = fetch_translated_question(question_id, lang)[0]
    translated_answer = fetch_translated_answers(answer_ids, lang)

    return question_id, translated_quest, translated_answer

def save_translated_questions(question_id, lang, translated_question, translated_answers):
    insert_translated_questions(question_id, lang, translated_question, translated_answers)

def create_question(question_title, category, difficulty, answers):
    insert_question_transaction(question_title, category, difficulty, answers)