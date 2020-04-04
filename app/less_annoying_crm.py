import json
import time

import requests
from selenium.webdriver import ActionChains

from app import logger, driver, wait, ec
from app.config import Config
from app.convertkit import ConvertKit


class Api:
    def __init__(self, timeout=15):
        self.timeout = timeout

    """ commented out cuz api doesn't work
    def get_request(self, url):
        response = requests.request("GET", url)
        if response.status_code != 200:
            error_msg = json.loads(response.content)
            logger.exception(f"Failed API request. Reason:\n\t{error_msg}")
        else:
            resp_json = json.loads(response.content)
            return resp_json
    """


class LessAnnoyingCrmUI:
    def login(self):
        logger.info("Logging in to LAC ...")
        driver.get("https://www.lessannoyingcrm.com/login/")

        email_elem = driver.find_element_by_id("Email")
        pw_elem = driver.find_element_by_id("Password")
        login_btn_elem = driver.find_element_by_id("Login")

        email_elem.send_keys(Config.LAC_USER)
        pw_elem.send_keys(Config.LAC_PW)
        login_btn_elem.click()

    def export_contacts(self):
        wait.until(ec.visibility_of_all_elements_located)

        # the export btn is on this page
        browse_url = "https://www.lessannoyingcrm.com/app/Browse"
        driver.get(browse_url)

        time.sleep(4)

        # find the 'Export' btn/link
        all_a_elems = driver.find_elements_by_tag_name("a")
        for a in all_a_elems:
            if "Export" in a.text:
                actions = ActionChains(driver)
                actions.move_to_element(a)  # must hover over before click works
                actions.click()
                actions.perform()

                logger.info("\n*** clicking export ... ***\n")
                a.click()
                time.sleep(20)
            logger.info(f"Exported contacts: {exported_contacts}")


class LessAnnoyingCRM(Api):
    def __init__(self, timeout=15):
        self.timeout = timeout
        # self.current_users = self.get_current_contacts()
        self.current_users = []
        self.previous_users = []
        # self.previous_users = self.get_historical_contacts()
        self.new_user_data = []
        # self.new_user_data = self.get_new_user_data()
        self.lac_ui = LessAnnoyingCrmUI()

        self.api_base = f"https://api.lessannoyingcrm.com/?UserCode={Config.LAC_API_USER_CODE}&APIToken={Config.LAC_API_TOKEN}"

    def get_historical_contacts(self):
        with open(Config.LAC_HIST_USERS_FILE, "r+") as f:
            hist_contacts = f.read()
        return hist_contacts

    # def get_current_contacts(self):
    #     url = f"{self.api_base}&Function=SearchContacts&RecordType=Contacts"
    #     all_contacts = self.get_request(url)
    #
    #     # resp = self.get_request(url)
    #     return all_contacts

    def get_current_contacts(self):
        self.lac_ui.login()
        time.sleep(4)
        self.lac_ui.export_contacts()

    def get_new_user_data(self):
        new_users_data = []

        for curr_user in self.current_users:
            if curr_user not in self.previous_users:
                new_users_data.append({
                    "first_name": curr_user["FirstName"],
                    "email": curr_user["Email"]["Text"]
                })
        return new_users_data

    def add_any_new_users_to_convertkit(self):
        if self.new_user_data:
            logger.info("New LAC users found. Adding to convertkit...")
            self._add_new_users_to_convertkit()
        else:
            logger.info("No new LAC users since last time")

    def _add_new_users_to_convertkit(self):
        new_subs_info = []
        for new_lac_user in self.new_user_data:
            new_sub_data = {
                "first_name": new_lac_user["first_name"],
                "email": new_lac_user["email"]
            }
            new_subs_info.append(new_sub_data)

        ck = ConvertKit()
        ck.add_subscribers(new_subs_info)


if __name__ == "__main__":
    LAC = LessAnnoyingCRM()
    LAC.get_current_contacts()
    LAC.add_any_new_users_to_convertkit()
