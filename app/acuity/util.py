from datetime import datetime
import shutil
from csv_diff import load_csv, compare
from app.config import Config
from app import logger, driver
import time
import os


def archive_current_acuity_csv():
    """
    ensures that the list.csv is renamed (so no save issues next time)
    ensures that hist file is correctly named, so can read next time
    :return:
    """
    logger.info("Archiving Acuity users csv ...")
    try:
        os.rename(Config.ACUITY_CURR_FILE_PATH, Config.ACUITY_HIST_FILE_PATH)
    except FileNotFoundError as fe:
        logger.warning(f"Could not find file, so skipping.\n{fe}")


def compare_prev_and_curr_acuity_users():
    logger.info("Comparing previous & current Acuity users ...")

    ############
    # get data #
    ############
    time.sleep(5)  # buffer for export file to finish download

    if not os.path.exists(Config.ACUITY_HIST_FILE_PATH):
        logger.info("No hist users file for Acuity.")
        logger.info("Creating hist users file with current users.")
        shutil.copyfile(Config.ACUITY_CURR_FILE_PATH, Config.ACUITY_HIST_FILE_PATH)

    compare_out = compare(
        load_csv(open(Config.ACUITY_HIST_FILE_PATH)),
        load_csv(open(Config.ACUITY_CURR_FILE_PATH))
    )

    added_data, removed_data = get_added_and_removed_data(compare_out)
    return added_data, removed_data


def export_acuity_users_to_csv():
    logger.info("Exporting client data ...")
    export_url = "https://secure.acuityscheduling.com/clients.php?action=bulk&op=exportExcelAll"
    driver.get(export_url)


def get_added_and_removed_data(compare_out):
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


def login_to_acuity():
    logger.info("Logging in to acuity ...")
    driver.get("https://secure.acuityscheduling.com/login.php")

    username_elem = driver.find_element_by_class_name("input-email")
    password_elem = driver.find_element_by_class_name("input-password")

    username_elem.send_keys(Config.ACUITY_USER)
    password_elem.send_keys(Config.ACUITY_PW)

    submit_btn = driver.find_element_by_class_name("input-login")
    submit_btn.click()
