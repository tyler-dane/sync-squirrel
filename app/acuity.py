import webbrowser
from app import logger, driver, wait, ec
from app.config import Config


def login():
    logger.info("Logging in ...")
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


def new_users_created_since_last_check():
    logger.info("Checking if any new users created ...")

    if not historical_data_exists():
        pass

    return True


def historical_data_exists():
    pass


if __name__ == "__main__":
    login()
    export_all_users_to_csv()
    if new_users_created_since_last_check():
        pass
