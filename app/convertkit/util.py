import os
import json
from app.config import Config
from app.convertkit.metadata import CkMetadata


def prev_users_file_exists():
    return os.path.isfile(Config.CONVERT_PREV_USERS_PATH)


def save_users_to_prev_users_file(users):
    """
    overwrites any existing content
    :param users: json data to save
    :return:
    """
    json_data = json.dumps(users)
    with open(Config.CONVERT_PREV_USERS_PATH, "w") as f:
        f.write(json_data)


def get_previous_convertkit_users():
    with open(Config.CONVERT_PREV_USERS_PATH, "r") as prev_ck_f:
        raw_hist_users = prev_ck_f.read()

    hist_users = json.loads(raw_hist_users)

    return hist_users


def get_new_users_data(curr_users, prev_users):
    new_user_data = []

    m = CkMetadata()

    for user in curr_users:
        if user not in prev_users:
            # keys match what LAC needs - values match what CK API provides
            user_id = user["id"]
            metadata_note = m.get_user_metadata_note(
                ck_id=user_id, ck_email=user["email_address"])

            user_data = {
                "first_name": user["first_name"],
                "last_name": "FromConvertKit",
                "email": user["email_address"],
                "note": metadata_note
            }
            new_user_data.append(user_data)

    return new_user_data
