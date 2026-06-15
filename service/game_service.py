import datetime

from quiz_app.validation import validate_answer_choice
from quiz_app.game_rules import give_help, win_rule
from quiz_app.repository.game_repo import (fetch_session_history, fetch_current_finished,
                                           fetch_answers_history, insert_answers_history,
                                           fetch_current_question_id, update_current_score,
                                           fetch_current_score, create_session_record,
                                           finish_session_record, insert_current_state,
                                           fetch_active_state_by_session_id, update_current_question,
                                           fetch_answers_by_user_id, fetch_current_state_by_user_id,
                                           fetch_answers_by_session_id, fetch_active_current_states,
                                           update_help_50_50, update_help_change_quest,
                                           fetch_current_help_change_quest, fetch_current_help_50_50)
from quiz_app.logger import logger
from quiz_app.repository.question_pero import fetch_correct_answer

def check_current_state_active(session_id):
    is_active = fetch_active_state_by_session_id(session_id)
    return is_active

def is_winner(score):
    won = win_rule(score)
    return won

def get_help(answer_variants, question_id):
    correct_variant = fetch_correct_answer(question_id)[0]

    wrong_variants = give_help(answer_variants, correct_variant)

    helped = {}
    for k, v in answer_variants.items():
        if not v in wrong_variants.values():
            helped[k] = v

    return helped

def this_time_game():
    now = datetime.datetime.now()
    return now

def spent_time(start, end):
    spent = end - start
    return int(spent.total_seconds())

def start_session(user):
    if type(user) == dict:
        user_id = user[0]
        first_name = user[1]
    else:
        user_id = user.id
        first_name = user.first_name

    now = this_time_game()
    started_at = now.strftime("%Y-%m-%d %H:%M:%S")

    session_id = create_session_record(user_id, started_at)

    insert_current_state(session_id, user_id)

    logger.info(f"User {user_id} ({first_name}) Started game")

    return session_id, now

def update_current_questions(session_id, question_id):
    update_current_question(session_id, question_id)

def update_current_scores(session_id, current_score):
    update_current_score(session_id, current_score)

def help_change_quest_used(session_id, user):
    update_help_change_quest(session_id)

    logger.info(f"User {user.id} ({user.first_name}) used help to change quest")

def help_50_50_used(session_id, user):
    update_help_50_50(session_id)

    logger.info(f"User {user.id} ({user.first_name}) used help 50/50")

def get_current_question(session_id):
    question = fetch_current_question_id(session_id)[0]

    return question

def get_current_score(session_id):
    current_score = fetch_current_score(session_id)[0]

    return current_score

def check_current_help_change_quest(session_id):
    help_count = fetch_current_help_change_quest(session_id)[0]

    if not help_count > 0:
        return False, help_count

    return True, help_count

def check_current_help_50_50(session_id):
    help_count = fetch_current_help_50_50(session_id)[0]

    if not help_count > 0:
        return False, help_count

    return True, help_count

def get_current_state_by_user_id(user_id):
    state = fetch_current_state_by_user_id(user_id)
    if not state:
        return None, "Inactive"

    session_id = state[0]
    active = state[1]
    return session_id, active

def is_current_state_finished(session_id):
    finished = fetch_current_finished(session_id)[0]

    finished = bool(finished)

    return finished

def finish_game(session_id, user, final_score, start_time):
    if type(user) == dict:
        user_id = user[0]
        first_name = user[1]
    else:
        user_id = user.id
        first_name = user.first_name

    end_time = this_time_game()
    finished_at = end_time.strftime("%Y-%m-%d %H:%M:%S")

    spent = spent_time(start_time, end_time)

    if is_winner(final_score):
        finish_session_record(session_id, user_id, final_score, finished_at, spent, 1)

        logger.info(f"User {user_id} ({first_name}) finished game with Win")
    else:
        finish_session_record(session_id, user_id, final_score, finished_at, spent)
        logger.info(f"User {user_id} ({first_name}) finished game with score {final_score}")

    return spent

def submit_answer(user_answer, answer_choices=None):
    validate_answer_choice(user_answer, answer_choices)

def save_answer(session_id, question_id, variant_id, is_correct):
    now = this_time_game()
    answered_at = now.strftime("%Y-%m-%d %H:%M:%S")

    insert_answers_history(session_id, question_id, variant_id, answered_at, is_correct)

def get_all_answers_history():
    history = fetch_answers_history()
    return history

def get_answers_by_user_id(user_id):
    answers = fetch_answers_by_user_id(user_id)
    return answers

def get_all_sessions_history():
    history = fetch_session_history()
    return history

def get_answers_by_session_id(session_id):
    answers = fetch_answers_by_session_id(session_id)
    return answers

def get_active_plays():
    states = fetch_active_current_states()
    return states

def get_sessions_list():
    sessions = get_all_sessions_history()

    session_list = f"========== SESSIONS ==========\n"

    sessions = reversed(sessions)

    for sid, real_name, u_name, score, time, spent in sessions:
        if score < 10:
            is_won = "LOST"
        else:
            is_won = "WON"

        minutes, seconds = divmod(spent, 60)
        if not u_name:
            user_name = "Unknown"
        else:
            user_name = "@" + u_name

        session_list += (f"\n------------ Session {sid} ------------"
                         f"\nReal Name - {real_name} "
                         f"\nUser Name - {user_name}"
                         f"\nScore - {score}/10 | {int(minutes)} min {int(seconds)} sec"
                         f"\nTime - {time}"
                         f"\n---------------- {is_won} ----------------\n")

    return session_list

def view_user_answers(session_id):
    currently_play = get_answers_by_session_id(session_id)
    active = check_current_state_active(session_id)

    active_play = f"========= Viewer Mode =========\n"

    for question, answer, correct in currently_play:
        is_correct = bool(correct)

        active_play += (f"\nQuestion - {question}"
                        f"\nAnswer - {answer}"
                        f"\nCorrect - {is_correct}\n")

    if not active:
        active_play += ("\n---------------------------"
                        "\nSession - finished")

    return active_play

def get_viewer_mode():
    active_players = get_active_plays()

    currently_playing = "Currently Active Players\n"

    if not active_players:
        currently_playing = "Currently, there is no any active plays!"
    else:
        for sess_id, us_id, r_name, u_name in active_players:
            if not u_name:
                user_name = "Unknown"
            else:
                user_name = "@" + u_name

            currently_playing += (f"\n------------- Session {sess_id} -------------"
                                  f"\nID - {us_id}"
                                  f"\nReal Name - {r_name}"
                                  f"\nUser Name - {user_name}"
                                  f"\n---------------------------------------")

    return currently_playing

def user_answers_by_id(user_id):
    answers = get_answers_by_user_id(user_id)

    answers_list = "\n========= ANSWERS =========\n"

    session_id = 0
    for sid, r_name, u_name, qu_id, ans_id, ans_title, time, correct in answers:

        correct = bool(correct)

        if not session_id == sid:
            session_id = sid

            answers_list += f"\n----------- Session {sid} -------------"

        if not correct:
            answers_list += (f"\nQuestion - {qu_id}/10"
                             f"\nAnswer - {ans_title} | {correct}"
                             f"\n{time}"
                             f"\n--------------- LOST ---------------\n")

        elif qu_id == 10 and correct:
            answers_list += (f"\nQuestion - {qu_id}/10"
                             f"\nAnswer - {ans_title} | {correct}"
                             f"\n{time}"
                             f"\n--------------- WON ---------------\n")
        else:
            answers_list += (f"\nQuestion - {qu_id}/10"
                             f"\nAnswer - {ans_title} | {correct}"
                             f"\n{time}\n")

    return answers_list