import os
import time
from datetime import datetime
from csv_diff import load_csv, compare

from app import logger, driver, convertkit
from app.config import Config
from app.convertkit import ConvertKit
from app.less_annoying_crm.lac import Lac


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


def compare_old_and_new_users(parent_dir):
    # these work together with brock lesner
    # first_path = os.path.join(parent_dir, "list_demo1.csv")
    # second_path = os.path.join(parent_dir, "list_added_one.csv")

    ############
    # get data #
    ############
    time.sleep(5)
    current_user_data = os.path.join(parent_dir, "list.csv")
    previous_user_data = os.path.join(parent_dir, "list_previous.csv")

    compare_out = compare(
        load_csv(open(previous_user_data)),
        load_csv(open(current_user_data))
    )

    ###############
    # format data #
    ###############
    added_users = compare_out["added"]
    removed_users = compare_out["removed"]

    # using emails as uids
    added_data = []
    removed_data = []

    for added in added_users:
        added_data.append({"email": added["Email"],
                           "first_name": added["First Name"],
                           "last_name": added["Last Name"]
                           })

    for removed in removed_users:
        removed_data.append({"email": removed["Email"],
                             "first_name": removed["First Name"],
                             "last_name": removed["Last Name"]
                             })

    return added_data, removed_data


def process_any_new_users(added_data, removed_data):
    new_user_added = False
    ###################
    # get email lists #
    ###################
    added_emails = []
    removed_emails = []

    for added in added_data:
        added_emails.append(added["email"])
    for removed in removed_data:
        removed_emails.append(removed["email"])

    ###########
    # compare #
    ###########
    subs_info = []
    for added_email in added_emails:
        if added_email not in removed_emails:
            ####################
            # process new user #
            ####################
            new_user_added = True
            logger.info(f"** processing new user with email '{added_email}'') **")

            # find user info #
            for added in added_data:
                if added["email"] == added_email:
                    subs_info.append({"first_name": added["first_name"],
                                      "last_name": added["last_name"],
                                      "email": added["email"]})

    if new_user_added:
        less_annoying_crm = Lac()
        less_annoying_crm.process_new_lac_users(user_info=subs_info)

        ck = ConvertKit()
        ck.add_subscribers(sub_info=subs_info)

    if not new_user_added:
        logger.info("No new users")


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


def archive_csv():
    logger.info("archiving old csv ...")
    os.rename("/Users/ty/Downloads/list.csv", f"/Users/ty/Downloads/{Config.ARCHIVE_CSV_NAME}")


if __name__ == "__main__":
    login()
    export_all_users_to_csv()
    added_data, removed_data = compare_old_and_new_users(parent_dir=Config.DOWNLOADS_DIR)
    process_any_new_users(added_data=added_data, removed_data=removed_data)
    archive_csv()
    # driver.quit()  # TODO add once working
