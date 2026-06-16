import datetime
from quiz_app.repository.user_repo import (insert_user, fetch_user_by_id,
                                           fetch_user_active_by_id, fetch_users_active,
                                           update_deactivate_user, update_activate_user,
                                           fetch_all_users)
from quiz_app.logger import logger

from quiz_app.validation import validate_user_id, validate_language
from quiz_app.locales.messages import msg
from quiz_app.config import ADMIN_ID

def register_user(user_id, first_name, user_name, lang):
    validate_user_id(user_id)
    validate_language(lang)

    if user_id == ADMIN_ID:
        role = "admin"
    else:
        role = "user"

    user = get_user_by_id(user_id)

    if user:
        raise ValueError("User already exists")

    created_at = this_time_user()

    insert_user(user_id, first_name, user_name, role, lang, created_at)

    logger.info(f"User {user_id} ({first_name}) registered")

def get_user_by_id(user_id):
    validate_user_id(user_id)

    user = fetch_user_by_id(user_id)

    return user

def get_all_users():
    users = fetch_all_users()
    return users

def get_users_active():
    active = fetch_users_active()
    return active

def get_one_user_active(user_id):
    active = fetch_user_active_by_id(user_id)
    return active

def deactivate_user(user_id):
    validate_user_id(user_id)

    user_active = get_one_user_active(user_id)
    first_name = get_user_by_id(user_id)

    if not first_name:
        raise ValueError(f"User {user_id} not found")

    active = bool(user_active[0])

    if not active:
        logger.warning(f"User {user_id} ({first_name[1]}) already inactive")
        raise ValueError("User already inactive")

    update_deactivate_user(user_id)

    logger.info(f"User {user_id} ({first_name[1]}) deactivated")

def reactivate_user(user_id):
    validate_user_id(user_id)

    user_active = get_one_user_active(user_id)
    first_name = get_user_by_id(user_id)

    if not first_name:
        raise ValueError(f"User {user_id} not found")

    active = bool(user_active[0])

    if active:
        logger.warning(f"User {user_id} ({first_name[1]}) already active")
        raise ValueError("User already active")

    update_activate_user(user_id)

    logger.info(f"User {user_id} ({first_name[1]}) reactivated")

def get_users_list():
    users = get_all_users()
    users_list = "========= USERS =========\n"

    user = 0
    for uid, f_name, u_name, created_at in users:
        active = get_one_user_active(uid)[0]

        user += 1
        if not u_name:
            u_name = "Unknown"

        active = bool(active)

        if active:
            activeness = "Active"
            signal = "🟢"
        else:
            activeness = "Inactive"
            signal = "🔴"

        users_list += (f"\n----------- User {user} ------------"
                       f"\n🆔 - {uid}"
                       f"\n👤 Name - {f_name}"
                       f"\n🏷 Username - {u_name}"
                       f"\n{signal} Status - {activeness}\n")

    return users_list

def this_time_user():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

def is_admin(user_id):
    if user_id == ADMIN_ID:
        return True

    return False

def greet(lang):
    now = datetime.datetime.now()
    clock = now.strftime("%H")

    hours = int(clock)

    greeting = ""

    if hours <= 3:
        greeting = f"{msg(lang, 'good_night')}"

    elif hours <= 11:
        greeting = f"{msg(lang, 'good_morning')}"

    elif hours <= 16:
        greeting = f"{msg(lang, 'good_afternoon')}"

    elif hours <= 21:
        greeting = f"{msg(lang, 'good_evening')}"

    elif hours <= 23:
        greeting = f"{msg(lang, 'good_night')}"

    return greeting