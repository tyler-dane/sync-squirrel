import time

from app import logger, driver, wait, ec, util
from app.config import Config


class ConvertKit:
    def __init__(self, first_name, email, sequences=Config.CONVERT_SEQ):
        self.first_name = first_name
        self.email = email
        self.sequences = sequences

    def login(self, username, password):
        logger.info("Logging in ...")
        driver.get("https://app.convertkit.com/users/login")

        username_elem = driver.find_element_by_id("user_email")
        password_elem = driver.find_element_by_id("user_password")

        username_elem.send_keys(username)
        password_elem.send_keys(password)

        submit_btn = "/html/body/div[1]/div/div[2]/div[2]/div/div/div[2]/form/button"
        driver.find_element_by_xpath(submit_btn).click()

    def add_single_subscriber(self):
        self.login(username=Config.CONVERT_USER, password=Config.CONVERT_PW)
        logger.info("adding subscriber ...")

        try:
            wait.until(ec.visibility_of_all_elements_located)
            wait.until(ec.presence_of_all_elements_located)

            add_subs_btn = driver.find_element_by_css_selector(".break > div:nth-child(1) > a:nth-child(1)")
            add_subs_btn.click()

            self.click_add_single_subscriber_btn()

        except Exception as e:
            logger.exception(e)
            driver.quit()

    def click_add_single_subscriber_btn(self):
        # TODO break out into smaller methods

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
        first_name_element.send_keys(self.first_name)
        email_element.send_keys(self.email)

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


if __name__ == "__main__":
    new_user_first_name = "Stan3"
    new_user_email = "foo@bar.com"

    ck = ConvertKit(first_name=new_user_first_name, email=new_user_email)
    ck.add_single_subscriber()

    driver.quit()

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
