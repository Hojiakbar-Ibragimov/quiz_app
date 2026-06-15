def validate_user_name(user_name):
    if not user_name.isalpha() or len(user_name) < 3 or user_name.strip() == "":
        raise ValueError("Invalid name")

def validate_user_id(user_id):
    if not str(user_id).isdigit():
        raise ValueError("Invalid ID")

    if int(user_id) <= 0:
        raise ValueError("Invalid ID")

def validate_answer_choice(choice, answer_choices):
    if answer_choices is None:
        valid_choices = {"a", "b", "c", "d", "h"}
    else:
        valid_choices = answer_choices.keys()

    choice = choice.lower().strip()

    if not choice in valid_choices:
        raise ValueError("Invalid choice!")

def validate_language(lang):
    if not lang.isalpha():
        raise ValueError("Invalid language")

    if len(lang) != 2:
        raise ValueError("Invalid language")