def check_answer(data):
    is_correct = data
    return bool(is_correct)

def win_rule(score):
    if score < 10:
        return False

    return True

def give_help(answer_variants, correct):
    cut_wrongs = 2

    wrongs = {}
    for k, v in answer_variants.items():
        if cut_wrongs > 0:
            if not v == correct:
                wrongs[k] = v
                cut_wrongs -= 1
    return wrongs

def questions_difficulty(question_level):
    difficulty = ""
    if question_level <= 3:
        difficulty = "easy"

    elif question_level <= 6:
        difficulty = "medium"

    elif question_level <= 10:
        difficulty = "hard"

    return difficulty