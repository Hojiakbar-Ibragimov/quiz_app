from quiz_app.service.user_service import (register_user, get_user_by_id, is_admin,
                                           deactivate_user, reactivate_user, get_users_list)
from quiz_app.service.profile_service import (get_users_profiles, get_user_played,
                                              get_rating, get_user_profile)
from quiz_app.service.game_service import (update_current_question, start_session,
                                            check_current_help_50_50, update_current_score,
                                           get_current_score, get_all_sessions_history,
                                           get_all_answers_history, finish_game, submit_answer,
                                           save_answer, is_winner, get_help, view_user_answers, get_viewer_mode,
                                           is_current_state_finished, update_help_50_50)
from quiz_app.service.question_service import (get_question_and_answers, get_answer_by_id,
                                               get_answers_id, check_answer_correctness)
def start_game(user):
    played = get_user_played(user[0])
    print(f"\nPlayed: {played}\nDear {user[1]}, game started!")

    session_id, start_time = start_session(user)

    next_quest_flow(user, session_id, start_time)

def next_quest_flow(user, session, this_time):
    while True:
        current_score = get_current_score(session)
        finished = is_current_state_finished(session)

        if is_winner(current_score):
            final_score = current_score
            spent_time = finish_game(session, user, final_score, this_time)

            show_game_result_to_user(user[1], final_score, spent_time)
            print(color("YOU WON!!!", 93))
            break

        if finished:
            break

        question_id, question, answers = get_question_and_answers(current_score + 1)

        update_current_question(session, question_id)

        while True:
            get_quests(question, answers, current_score)

            answers_id = get_answers_id(question_id)
            answer_variants = {
                "a": answers_id[0][0],
                "b": answers_id[1][0],
                "c": answers_id[2][0],
                "d": answers_id[3][0]
            }

            try:
                user_answer = input("\n>>> ")
                submit_answer(user_answer)
            except ValueError as e:
                print(e)
                continue

            if user_answer == 'h':
                help_50_50, count = check_current_help_50_50(session)
                try:
                    if not help_50_50:
                        raise ValueError("50/50 help was used!")

                    new_variants = get_help(answer_variants, question_id)
                    helped = show_help_answers(current_score, question, new_variants)
                    update_help_50_50(session)

                    user_answer = input("\n>>>")
                    submit_answer(user_answer, helped)
                except ValueError as e:
                    print(e)
                    continue

            user_answer = user_answer.lower()

            is_correct = check_answer_correctness(answer_variants[user_answer])

            save_answer(session, question_id,
                        answer_variants[user_answer], is_correct)

            if is_correct:
                current_score += 1
                update_current_score(session, current_score)

                print(color("Correct!", 92))
                break
            else:
                final_score = current_score
                spent_time = finish_game(session, user, final_score, this_time)

                print(color("Wrong!", 91))
                show_game_result_to_user(user[1], final_score, spent_time)
                break


def get_quests(question, answers, current_score):
    print(color(f"\nquestion {current_score + 1}/10", 94))
    print(f"\n{question}\n\n"
          f"A) {answers[0][1]}\n"
          f"B) {answers[1][1]}\n"
          f"C) {answers[2][1]}\n"
          f"D) {answers[3][1]}\n"
          f"H - Help")

    return question

def show_help_answers(current_score, question, helped_variants):

    print(color(f"\nquestion {current_score + 1}/10", 94))
    print(f"\n{question}\n\n")

    for k, v in helped_variants.items():
        title = get_answer_by_id(v)
        print(f"{k.upper()}) {title}")

    return helped_variants

def color(text, code):
    return f"\033[{code}m{text}\033[0m"

def color_score(score):
    if score <= 3:
        final_score = color(score, 91)
    elif score <= 6:
        final_score = color(score, 94)
    elif score <= 10:
        final_score = color(score, 92)
    else:
        return color('unknown', 31)

    return final_score

def show_game_result_to_user(user, final_score, spent_time):
    minutes, seconds = divmod(spent_time, 60)

    score = color_score(final_score)

    print(f"\nDear {user}"
          f"\nYour final score: {score}"
          f"\nSpent: {minutes} minutes {seconds} seconds")

def formatting_session_history():
    sessions = get_all_sessions_history()
    print(f"\n{'SESSION ID':<20}{'REAL NAME':<20}{'USER NAME':<20}"
          f"{'SCORE':<20}{'TIME':<25}{'SPENT':<25}\n")
    for sid, r_name, u_name, score, started_time, spent in sessions:
        if not u_name:
            u_name = "Unknown"
        score = color_score(score)

        print(f"{sid:<20}{r_name:<20}{u_name:<20}{score:<20}"
              f"{started_time:<25}{spent} seconds")

def formatting_answers_history():
    answers = get_all_answers_history()
    print(f"\n{'SESSION ID':<20}{'REAL NAME':<20}{'QUESTION':<20}"
          f"{'SELECTED ANSWER':<20}{'CORRECTNESS':<20}{'ANSWERED AT':<20}\n")
    for sess_id, u_name, quest, answer, time, correct in answers:
        is_correct = bool(int(correct))

        if is_correct:
            correctness = color(is_correct, 92)
        else:
            correctness = color(is_correct, 91)

        print(f"{sess_id:<20}{u_name:<20}{quest:<20}{answer:<20}{correctness:<20}{time:<20}")


def main():
    while True:
        first_menu()
        choice = input("choose: ")
        if choice == "1":
            try:
                user_id = int(input(f"enter user ID: "))
                user = get_user_by_id(user_id)

                if not user:
                    raise ValueError("User not found")

                if is_admin(user_id):
                    admin_panel()
                else:
                    user_interface(user_id)

            except ValueError as e:
                print(e)
                continue

        elif choice == '2':
            try:
                user_id = int(input("enter ID: "))
                first_name = input("enter real name: ")
                user_name = input("enter user name: ")
                lang = input("enter language (en, uz): ")

                register_user(user_id, first_name, user_name, lang)

                user_interface(user_id)

                print("Welcome to our team")
            except ValueError as e:
                print(e)

        elif choice == "0":
            break

        else:
            print("Wrong choice")

def user_interface(user_id):
    while True:
        users_menu()
        choice = input(">>> ")

        if choice == "1":
            user = get_user_by_id(user_id)
            start_game(user)

        elif choice == "2":
            print(get_rating(user_id))

        elif choice == "3":
            print(get_user_profile(user_id))

        elif choice == "0":
            break

        else:
            print("Wrong choice")

def admin_panel():
    while True:
        admin_menu()
        choice = input(">>> ")

        if choice == "1":
            control_users()

        elif choice == "2":
            print(get_users_profiles())

        elif choice == "3":
            while True:
                view = get_viewer_mode()
                print(view)
                try:
                    session_id = int(input("session ID (or close - 0): "))

                    if session_id == 0:
                        break

                    viewer_mode(session_id)
                except ValueError as e:
                    print(e)
                    continue
        elif choice == "0":
            break

        else:
            print("Wrong choice, Sir")

def control_users():
    while True:
        print(get_users_list())
        print("1 - Deactivate"
              "\n2 - Reactivate"
              "\n0 - Back")
        choice = input("\n>>> ")

        if choice == "1":
            while True:
                try:
                    user_id = int(input("user ID (or close - 0): "))

                    if user_id == 0:
                        break

                    deactivate_user(user_id)

                    print(get_users_list())
                except ValueError as e:
                    print(e)
                    continue

        if choice == "2":
            while True:
                try:
                    user_id = int(input("user ID (or close - 0): "))

                    if user_id == 0:
                        break

                    reactivate_user(user_id)

                    print(get_users_list())
                except ValueError as e:
                    print(e)
                    continue

        if choice == "0":
            break

def viewer_mode(session_id):
    while True:
        print(view_user_answers(session_id))
        print("\n1 - 🔄️ Refresh"
              "\n0 - ⬅️ Back")

        choice = input("\n>>> ")

        if choice == "1":
            print(view_user_answers(session_id))
            print("\n1 - 🔄️ Refresh"
                  "\n2 - ⬅️ Back")

        elif choice == "0":
            break

        else:
            print("Wrong choice, Sir")

def first_menu():
    print("\n1 - sign in"
          "\n2 - sign up"
          "\n0 - exit\n")

def users_menu():
    print("\n1 - 🎮 Start Game"
          "\n2 - 🏆 Rating"
          "\n3 - 👤 Profile"
          "\n0 - ⬅️ Quit")

def admin_menu():
    print("\n1 - Control Users"
          "\n2 - 👤 Profiles"
          "\n3 - 🌐 Viewer Mode"
          "\n0 - ⬅️ Quit")