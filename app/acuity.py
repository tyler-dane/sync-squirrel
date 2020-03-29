import os
import time
from datetime import datetime
from csv_diff import load_csv, compare

from app import logger, driver, convertkit
from app.config import Config
from app.convertkit import ConvertKit


def login():
    logger.info("Logging in to acuity ...")
    driver.get("https://secure.acuityscheduling.com/login.php")

    username_elem = driver.find_element_by_class_name("input-email")
    password_elem = driver.find_element_by_class_name("input-password")

    username_elem.send_keys(Config.ACUITY_USER)
    password_elem.send_keys(Config.ACUITY_PW)

    submit_btn = driver.find_element_by_class_name("input-login")
    submit_btn.click()


def export_all_users_to_csv():
    logger.info("Exporting client data ...")
    export_url = "https://secure.acuityscheduling.com/clients.php?action=bulk&op=exportExcelAll"
    driver.get(export_url)


def process_new_users(parent_dir):
    # these work together with brock lesner
    # first_path = os.path.join(parent_dir, "list_demo1.csv")
    # second_path = os.path.join(parent_dir, "list_added_one.csv")

    time.sleep(5)
    current_user_data= os.path.join(parent_dir, "list.csv")
    previous_user_data = os.path.join(parent_dir, "list_previous.csv")

    compare_out = compare(
        load_csv(open(previous_user_data)),
        load_csv(open(current_user_data))
    )

    if len(compare_out["added"]) > len(compare_out["removed"]):
        new_users = get_new_users_data(added_users=compare_out["added"], removed_users=compare_out["removed"])
        import_new_users_to_convertkit(new_users=new_users)



def get_new_users_data(added_users, removed_users):
    new_user_data = []

    # using emails as uids
    added_emails = []
    removed_emails = []

    for added in added_users:
        added_emails.append(added["Email"])
    for removed in removed_users:
        removed_emails.append(removed["Email"])

    for added in added_users:
        if added["Email"] not in removed_emails:
            print(f"found new user (has email {added['Email']})")
            new_user_data.append({
                "email": added["Email"],
                "first_name": added["First Name"]
            })

    return new_user_data


def get_new_filename():
    logger.info("Checking if any new users created ...")

    for file in os.listdir(Config.DOWNLOADS_DIR):
        if "list.csv" in file:  # acuity's default filename
            now = datetime.now()
            timestamp = now.strftime("%Y-%m-%dT%H%M%S")
            new_filename = f"list_{timestamp}.csv"
            os.rename(file, new_filename)
            return new_filename
        else:
            logger.exception(f"No CSV file found")

    return True


def import_new_users_to_convertkit(new_users):
    for user in new_users:
        first_name = user["first_name"]
        email = user["email"]
        ck = ConvertKit(first_name=first_name, email=email)
        ck.add_single_subscriber()


def archive_csv():
    logger.info("archiving old csv ...")
    os.rename("/Users/ty/Downloads/list.csv", f"/Users/ty/Downloads/{Config.ARCHIVE_CSV_NAME}")


if __name__ == "__main__":
    login()
    export_all_users_to_csv()
    process_new_users(parent_dir=Config.DOWNLOADS_DIR)
    archive_csv()
