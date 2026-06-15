import requests, random, html
from quiz_app.service import create_question, translate, get_questions_with_limit, get_answers, save_translated_questions

def import_questions():
    for _ in range(100):
        response = requests.get(
            "https://opentdb.com/api.php?amount=50&type=multiple"
        )

        data = response.json()

        if "results" in data:
            for result in data["results"]:
                question = html.unescape(result["question"])
                category = result["category"]
                difficulty = result["difficulty"]

                correct = html.unescape(
                    result["correct_answer"]
                )

                incorrect = [
                    html.unescape(answer)
                    for answer in result["incorrect_answers"]
                ]

                all_answers = [
                    correct,
                    *incorrect
                ]

                random.shuffle(all_answers)

                answers = []
                for answer in all_answers:
                    if answer == correct:
                        item = (answer, 1)
                        answers.append(item)
                    else:
                        item = (answer, 0)
                        answers.append(item)

                create_question(question, category, difficulty, answers)


def translate_questions(lang):
    offset = 0

    if not len(lang) == 2:
        return False

    while True:
        try:
            questions = get_questions_with_limit(offset)

        except Exception as e:
            print(e)
            break

        if not questions:
            print("translation ended")
            break

        for question in questions:
            try:
                question_id = question[0]
                question_title = question[1]

                translated_question = translate(question_title, lang)

                answers = get_answers(question_id)

                all_answers = []
                for answer in answers:
                    answer_id = answer[0]
                    answer_title = answer[1]

                    uz_answer = translate(answer_title, lang)
                    item = (answer_id, uz_answer)
                    all_answers.append(item)

                save_translated_questions(question_id, lang, translated_question, all_answers)

                print(f"Translated question - {question[0]}")

            except Exception as e:
                print(e)
                continue

        offset += 100