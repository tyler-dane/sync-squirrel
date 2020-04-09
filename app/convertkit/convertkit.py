import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from app import logger, driver, wait, ec, util
from app.config import Config
from app.less_annoying_crm.lac import Lac


class ConvertKit:
    def __init__(self, sequences=Config.CONVERT_SEQ):
        self.sequences = sequences
        self.logged_in = False

    def login(self, username, password):
        logger.info("Logging in ...")
        driver.get("https://app.convertkit.com/users/login")

        username_elem = driver.find_element_by_id("user_email")
        password_elem = driver.find_element_by_id("user_password")

        username_elem.send_keys(username)
        password_elem.send_keys(password)

        submit_btn = "/html/body/div[1]/div/div[2]/div[2]/div/div/div[2]/form/button"
        driver.find_element_by_xpath(submit_btn).click()

    def add_subscribers(self, sub_info):
        logged_in = False

        for sub in sub_info:
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
        # TODO Finish
        curr_users = self.get_current_convertkit_users()
        prev_users = self.get_previous_convertkit_users()

        if len(curr_users) > len(prev_users):
            logger.info("New ConvertKit users found. Adding them to Less Annoying CRM ...")
            new_users = self._get_new_user_data(curr_users=curr_users, prev_users=prev_users)

            less_annoying_crm = Lac()
            less_annoying_crm.process_new_lac_users(user_info=new_users)

        else:
            logger.info("No new ConvertKit users")

    def get_current_convertkit_users(self):
        # TODO
        curr_users = "api request"
        return curr_users

    def get_previous_convertkit_users(self):
        return "read from .json"

    def _get_new_user_data(self, curr_users, prev_users):
        # TODO
        new_user_data = []
        for user in curr_users:
            if user not in prev_users:
                # keys match what LAC needs - values match what CK API provides
                user_id = ""
                users_ck_channels = self._get_note_about_users_ck_channels(ck_id=user_id)

                user_data = {
                    "first_name": user["first_name"],
                    "last_name": "FromConvertKit",
                    "email": user["email_address"],
                    "note": users_ck_channels
                }

        return new_user_data

    def _get_note_about_users_ck_channels(self, ck_id):
        channels = []
        resp = f"api request to /v3/subscribers/{ck_id}/tags"
        for chan in resp:
            channels.append(chan)

        channels_note = f"This user belongs to these ConvertKit channels: {channels}"
        return channels_note


if __name__ == "__main__":
    ck = ConvertKit()
    ck.add_any_new_users_to_lac()

"""
NOTES

# THESE WORK
    # sub_demo_works = wait.until(ec.element_to_be_clickable((By.ID, "subscribers-select-all")))
    # search_btn = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/section/div/section[1]/form/input[4]").click()

    # TESTING THESE
    # add_sub_btn = wait.until(ec.element_to_be_clickable((By.ID, "addSubscribersButton")))
    # add_sub_btn = wait.until(ec.visibility_of_element_located((By.ID, "addSubscribersButton")))
    # wait.until(ec.presence_of_all_elements_located)
    # add_sub_btn = wait.until(ec.visibility_of_element_located((By.XPATH, "//*[@id='addSubscribersButton']")))
    # add_sub_btn.click()


---- selecting subs
all_as_test = util.get_all_text_from_html_tag("a")
        all_is_test = util.get_all_text_from_html_tag("i")
        all_a_elems = driver.find_elements_by_tag_name("a")
        for a_elem in all_a_elems:
            if "single subscriber" in a_elem.text:
                a_elem.click()

# span_elem = driver.find_elements_by_tag_name("span")
        # span_text = []
        # for span in span_elem:
        #     span_text.append(span.text)
        # label_elems = driver.find_elements_by_tag_name("label")


"""
