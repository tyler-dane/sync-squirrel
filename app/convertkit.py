import time

from app import logger, driver, wait, ec, util
from app.config import Config


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

            logger.info("adding subscriber ...")

            try:
                wait.until(ec.visibility_of_all_elements_located)
                wait.until(ec.presence_of_all_elements_located)
                time.sleep(5) # TODO testing

                add_subs_btn = driver.find_element_by_css_selector(".break > div:nth-child(1) > a:nth-child(1)")
                add_subs_btn.click()

                self._click_add_single_subscriber_btn_and_proceed(first_name=sub["first_name"], email=sub["email"])

            except Exception as e:
                logger.exception(e)
                driver.quit()

    def _click_add_single_subscriber_btn_and_proceed(self, first_name, email):
        # TODO break out into smaller methods
        # TODO add check to make sure user doesn't already exist - otherwise can't save

        # time.sleep(5)
        driver.implicitly_wait(10)  # explicit wait wasnt working for single sub btn

        single_sub_btn = driver.find_element_by_class_name("btn--step--single-sub")
        single_sub_btn.click()

        ########################
        # enter name and email #
        ########################
        # wait(ec.presence_of_all_elements_located)
        driver.implicitly_wait(10)
        first_name_element = driver.find_element_by_id("first-name")
        email_element = driver.find_element_by_id("email")

        #####################
        # add subscriber(s) #
        #####################
        # TODO clear existing before sending
        # currently first user is cached and second is concated;
        # TestUser1TestUser2
        # test@aol.comtest2@new.rr.com <--breaks cuz not valid email
        first_name_element.send_keys(first_name)
        email_element.send_keys(email)

        # find Sequences dropdown
        all_em_elems = driver.find_elements_by_tag_name("em")
        reasonable_opts = []
        for em_elem in all_em_elems:
            if "0 of " in em_elem.text:
                reasonable_opts.append(em_elem)

        # click dropdown
        sequences_dropdown = reasonable_opts[1]  # 0 = Forms; 1 = Sequences; 2 = Tags
        sequences_dropdown.click()

        # click sequence checkbox
        label_elems = driver.find_elements_by_tag_name("label")
        for label in label_elems:
            for seq_name in self.sequences:
                if seq_name in label.text:
                    label.click()
                    break

        self.click_save_subscriber_btn()

    def click_save_subscriber_btn(self):
        add_sub_save_btn = "/html/body/div[1]/div/div[2]/div/div[2]/div/div[1]/div/form/button"  # TODO use relative xpath
        driver.find_element_by_xpath(add_sub_save_btn).click()
        foo = ""


# if __name__ == "__main__":
    # new_user_first_name = "Stan3"
    # new_user_email = "foo@bar.com"
    #
    # ck = ConvertKit()
    # ck.add_single_subscriber(first_name=new_user_first_name, email=new_user_email)
    #
    # driver.quit()

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
