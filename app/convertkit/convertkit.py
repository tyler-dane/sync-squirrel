import json
import os
import time
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from app import logger, driver, wait, ec, util
from app.config import Config
from app.convertkit.ck_api import ConvertKitApi
from app.convertkit.metadata import CkMetadata


class ConvertKit:
    def __init__(self, sequences=Config.CONVERT_SEQ):
        self.sequences = sequences
        self.logged_in = False
        self.ck_api = ConvertKitApi()

    def login(self, username, password):
        logger.info("Logging in ...")
        driver.get("https://app.convertkit.com/users/login")

        username_elem = driver.find_element_by_id("user_email")
        password_elem = driver.find_element_by_id("user_password")

        username_elem.send_keys(username)
        password_elem.send_keys(password)

        submit_btn = "/html/body/div[1]/div/div[2]/div[2]/div/div/div[2]/form/button"
        driver.find_element_by_xpath(submit_btn).click()

    def add_users_to_ck(self, users_info):
        logged_in = False

        for sub in users_info:
            if logged_in is False:
                self.login(username=Config.CONVERT_USER, password=Config.CONVERT_PW)
                logged_in = True

            first_name = sub["first_name"]
            email = sub["email"]
            logger.info(f"\nadding subscriber ({email})...\n")

            try:
                wait.until(ec.visibility_of_all_elements_located)
                wait.until(ec.presence_of_all_elements_located)
                time.sleep(5)  # TODO testing

                self._click_add_subs_home_btn()
                self._click_add_single_sub_btn(first_name=first_name, email=email)
                self._enter_name_and_email(first_name=first_name, email=email)
                self._click_sequences_dropdown()
                self._click_sequences_checkboxes()
                self._click_save_subscriber_btn()

            except Exception as e:
                logger.exception(e)
                print("sleeping before quitting ...")
                time.sleep(10)
                driver.quit()

        # keep hist users file up-to-date
        curr_users = self.get_current_convertkit_users()
        self._save_users_to_prev_users_file(users=curr_users)

    def _click_add_subs_home_btn(self):
        logger.info("\nclicking Add Subscribers button ...\n")
        try:
            # try getting elem by id?
            add_subs_btn = driver.find_element_by_css_selector(".break > div:nth-child(1) > a:nth-child(1)")
            add_subs_btn.click()
        except (NoSuchElementException, TimeoutException) as ne:
            logger.info(f"\nretrying..\n")
            self._click_add_subs_home_btn()

    def _click_add_single_sub_btn(self, first_name, email):
        # TODO break out into smaller methods
        # TODO add check to make sure user doesn't already exist - otherwise can't save

        logger.info("\nClicking Add Single Subscriber button ...\n")
        try:
            time.sleep(4)
            driver.implicitly_wait(10)  # explicit driver wait wasnt working for single sub btn

            # this alone didnt fix, needed sleep
            # single_sub_btn = wait.until(ec.element_to_be_clickable((By.CLASS_NAME, "btn--step--single-sub")))
            single_sub_btn = driver.find_element_by_class_name("btn--step--single-sub")  # orig, worked but fickle
            print("***\nFound Single Sub Button\n***")
            single_sub_btn.click()
            print("!!! clicked singl sub button !!!")
            time.sleep(2)

        except (NoSuchElementException, TimeoutException) as ne:
            logger.info(f"\nretrying after {repr(ne)}..\n")
            time.sleep(2)
            self._click_add_single_sub_btn(first_name, email)

    def _enter_name_and_email(self, first_name, email):
        try:
            ########################
            # enter name and email #
            ########################
            # wait(ec.presence_of_all_elements_located)
            driver.implicitly_wait(10)
            # first_name_element = wait.until(ec.element_located_to_be_selected((By.ID, 'first-name')))  # testing
            print('\n**located first name elem**\n')

            first_name_element = driver.find_element_by_id("first-name")  # orig, broke
            email_element = driver.find_element_by_id("email")

            #####################
            # add subscriber(s) #
            #####################
            # TODO clear existing before sending
            # currently first user is cached and second is concated;
            # TestUser1TestUser2
            # test@aol.comtest2@new.rr.com <--breaks cuz not valid email
            first_name_element.clear()
            first_name_element.send_keys(first_name)
            email_element.send_keys(email)

        except (NoSuchElementException, TimeoutException) as ne:
            logger.info(f"\nFailed entering name & email. Trying again ...\n")
            time.sleep(1)
            self._enter_name_and_email(first_name, email)

    def _click_sequences_dropdown(self):
        try:
            # find Sequences dropdown
            all_em_elems = driver.find_elements_by_tag_name("em")
            reasonable_opts = []
            for em_elem in all_em_elems:
                if "0 of " in em_elem.text:
                    reasonable_opts.append(em_elem)

            # click dropdown
            sequences_dropdown = reasonable_opts[1]  # 0 = Forms; 1 = Sequences; 2 = Tags
            sequences_dropdown.click()

        except (NoSuchElementException, TimeoutException) as ne:
            logger.info(f"\nFailed clicking sequences dropdown. Trying again ...\n")
            time.sleep(1)
            self._click_sequences_dropdown()

    def _click_sequences_checkboxes(self):
        try:
            # click sequence checkbox
            label_elems = driver.find_elements_by_tag_name("label")
            for label in label_elems:
                for seq_name in self.sequences:
                    if seq_name in label.text:
                        label.click()
                        break
        except (NoSuchElementException, TimeoutException) as ne:
            logger.info(f"\nFailed clicking sequences checkboxes. Trying again ...\n")
            time.sleep(1)
            self._click_sequences_checkboxes()

    def _click_save_subscriber_btn(self):
        logger.info("\nClicking Save button ...\n")
        add_sub_save_btn = "/html/body/div[1]/div/div[2]/div/div[2]/div/div[1]/div/form/button"  # TODO use relative xpath
        driver.find_element_by_xpath(add_sub_save_btn).click()
        logger.info("\tClicked Save button")

    def add_any_new_users_to_lac(self):
        logger.info("""
        *******************************
        Syncing
            ConvertKit --> Less Annoying CRM
        *******************************
        """)

        # TODO fix so don't have to use local import and no circular top imports
        from app.less_annoying_crm.lac import Lac

        curr_users = self.get_current_convertkit_users()

        if self._prev_users_file_exists():
            prev_users = self.get_previous_convertkit_users()

            if len(curr_users) > len(prev_users):
                logger.info("New ConvertKit users found. Adding them to Less Annoying CRM ...")
                new_users = self._get_new_users_data(curr_users=curr_users, prev_users=prev_users)

                less_annoying_crm = Lac()
                less_annoying_crm.create_new_lac_user(users_info=new_users)

            else:
                logger.info("No new ConvertKit users")
        else:
            logger.info(
                "No previous users file for ConvertKit. Recording current users into historical file for next time")
            self._save_users_to_prev_users_file(users=curr_users)

    def get_current_convertkit_users(self):
        url = f"{self.ck_api.base}/subscribers?api_secret={self.ck_api.secret}"
        page_1_resp = self.ck_api.get_request(url=url)

        curr_users = page_1_resp["subscribers"]

        if page_1_resp["total_pages"] > 1:
            curr_page = int(page_1_resp["page"])
            next_page = curr_page + 1
            total_pages = page_1_resp["total_pages"]

            while curr_page < total_pages:
                next_page_url = f"{url}&page={next_page}"
                next_page_resp = self.ck_api.get_request(next_page_url)

                curr_users.extend(next_page_resp["subscribers"])

                curr_page += 1
                next_page += 1

        return curr_users

    def _prev_users_file_exists(self):
        return os.path.isfile(Config.CONVERT_PREV_USERS_PATH)

    def _save_users_to_prev_users_file(self, users):
        """
        overwrites any existing content
        :param users: json data to save
        :return:
        """
        json_data = json.dumps(users)
        with open(Config.CONVERT_PREV_USERS_PATH, "w") as f:
            f.write(json_data)

    def get_previous_convertkit_users(self):
        with open(Config.CONVERT_PREV_USERS_PATH, "r") as prev_ck_f:
            raw_hist_users = prev_ck_f.read()

        hist_users = json.loads(raw_hist_users)

        return hist_users

    def _get_new_users_data(self, curr_users, prev_users):
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


# if __name__ == "__main__":
#     ck = ConvertKit()
#     ck.add_any_new_users_to_lac()
