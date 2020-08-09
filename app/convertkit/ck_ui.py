import time
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as ec
from app import logger, driver, wait
from app import util as app_util
from app.config import Config
from app.convertkit.ck_api import ConvertKitApi


class ConvertKitUi:
    def __init__(self, sequences=Config.CONVERT_SEQ, max_retries=10, tags=Config.CONVERT_TAG):
        self.ck_api = ConvertKitApi()
        self.sequences = sequences
        self.tag = tags
        self.max_retries = max_retries
        self.logged_in = False

    def add_users_to_ck(self, users_info):
        for user in users_info:
            if not self.ck_api.user_exists(user_email=user["email"]):
                self._login_if_needed()

                first_name = user["first_name"]
                email = user["email"]
                logger.info(f"Adding CK subscriber ({email})...")

                try:
                    wait.until(ec.visibility_of_all_elements_located)
                    wait.until(ec.presence_of_all_elements_located)
                    time.sleep(Config.CONVERT_SLEEP_MED)

                    self._click_add_subs_home_btn()
                    self._click_add_single_sub_btn(first_name=first_name, email=email)
                    self._enter_name_and_email(first_name=first_name, email=email)

                    # using tags for demo
                    self._click_tags_dropdown()
                    self._click_tags_checkboxes()
                    # uncommented cuz need pro version for sequences
                    # self._click_sequences_dropdown()
                    # self._click_sequences_checkboxes()
                    self._click_save_subscriber_btn()

                    app_util.write_to_changelog(f"Created ConvertKit user: {email}")

                except Exception as e:
                    logger.exception(e)
                    print("sleeping before quitting ...")
                    time.sleep(Config.CONVERT_SLEEP_LONG)
                    driver.quit()

        # keep hist users file up-to-date
        curr_users = self.ck_api.get_current_convertkit_users()
        logger.info("Archiving current CK users ...")
        app_util.archive_curr_users(file=Config.CONVERT_PREV_USERS_PATH, curr_users=curr_users)

    def _login_if_needed(self):
        driver.get("https://app.convertkit.com")
        if driver.current_url == "https://app.convertkit.com/users/login":  # redirected
            self._login(username=Config.CONVERT_USER, password=Config.CONVERT_PW)
            self.logged_in = True

    def _login(self, username, password):
        logger.info("Logging in ...")
        driver.get("https://app.convertkit.com/users/login")

        username_elem = driver.find_element_by_id("user_email")
        password_elem = driver.find_element_by_id("user_password")

        username_elem.send_keys(username)
        password_elem.send_keys(password)

        all_btns = driver.find_elements_by_tag_name("button")
        for btn in all_btns:
            lower_btn_name = btn.text.lower()
            if "log in" in lower_btn_name:
                btn.click()

        # submit_btn_path = "/html/body/div[1]/div/div[2]/div[2]/div/div/div[2]/form/button"
        # submit_btn = driver.find_element_by_xpath(submit_btn_path)
        # submit_btn.click()

    def _click_add_subs_home_btn(self):
        logger.info("Clicking Add Subscribers button ...")
        try:
            # try getting elem by id?
            add_subs_btn = driver.find_element_by_css_selector(".break > div:nth-child(1) > a:nth-child(1)")
            add_subs_btn.click()
        except (NoSuchElementException, TimeoutException) as ne:
            logger.info(f"\nretrying..\n")
            self._click_add_subs_home_btn()

    def _click_add_single_sub_btn(self, first_name, email):
        # TODO add check to make sure user doesn't already exist - otherwise can't save

        logger.info("Clicking Add Single Subscriber button ...")

        curr_retry_count = 0
        if curr_retry_count < self.max_retries:

            try:
                time.sleep(Config.CONVERT_SLEEP_MED)
                driver.implicitly_wait(10)  # explicit driver wait wasnt working for single sub btn

                # this alone didnt fix, needed sleep
                # single_sub_btn = wait.until(ec.element_to_be_clickable((By.CLASS_NAME, "btn--step--single-sub")))
                single_sub_btn = driver.find_element_by_class_name("btn--step--single-sub")  # orig, worked but fickle
                single_sub_btn.click()
                time.sleep(Config.CONVERT_SLEEP_MED)

            except (NoSuchElementException, TimeoutException) as ne:
                curr_retry_count += 1
                logger.info(f"Retrying after {repr(ne)}..")
                time.sleep(2)
                self._click_add_single_sub_btn(first_name, email)

    def _enter_name_and_email(self, first_name, email):
        try:
            ########################
            # enter name and email #
            ########################
            # wait(ec.presence_of_all_elements_located)
            driver.implicitly_wait(Config.CONVERT_SLEEP_LONG)
            # first_name_element = wait.until(ec.element_located_to_be_selected((By.ID, 'first-name')))  # testing

            first_name_element = driver.find_element_by_id("first-name")  # orig, broke
            email_element = driver.find_element_by_id("email")

            #####################
            # add subscriber(s) #
            #####################
            first_name_element.clear()
            first_name_element.send_keys(first_name)
            email_element.send_keys(email)

        except (NoSuchElementException, TimeoutException) as ne:
            logger.info(f"\nFailed entering name & email. Trying again ...\n")
            time.sleep(1)
            self._enter_name_and_email(first_name, email)

    def _click_tags_dropdown(self):
        try:
            # find Sequences dropdown
            all_em_elems = driver.find_elements_by_tag_name("em")
            reasonable_opts = []
            for em_elem in all_em_elems:
                if "0 of " in em_elem.text:
                    reasonable_opts.append(em_elem)

            # click dropdown
            tags_dropdown = reasonable_opts[2]  # 0 = Forms; 1 = Sequences; 2 = Tags
            tags_dropdown.click()
        except (NoSuchElementException, TimeoutException) as ne:
            logger.info(f"\nFailed clicking tags dropdown. Trying again ...\n")
            time.sleep(1)
            self._click_tags_dropdown()

    def _click_tags_checkboxes(self):
        try:
            # click tag checkbox
            label_elems = driver.find_elements_by_tag_name("label")
            for label in label_elems:
                if self.tag in label.text:
                    label.click()
                    break

        except (NoSuchElementException, TimeoutException) as ne:
            logger.info(f"\nFailed clicking sequences checkboxes. Trying again ...\n")
            time.sleep(1)
            self._click_sequences_checkboxes()

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
        logger.info("Clicking Save button ...")
        add_sub_save_btn = "/html/body/div[1]/div/div[2]/div/div[2]/div/div[1]/div/form/button"  # TODO use relative xpath
        driver.find_element_by_xpath(add_sub_save_btn).click()
        logger.info("Clicked Save button")
