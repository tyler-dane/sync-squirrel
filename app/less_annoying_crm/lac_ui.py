from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver import ActionChains
from app import logger, driver, wait, ec
from app.config import Config
import time


class LacUI:
    def __init__(self):
        pass

    def login(self):
        logger.info("Logging in to LAC ...")
        driver.get("https://www.lessannoyingcrm.com/login/")

        email_elem = driver.find_element_by_id("Email")
        pw_elem = driver.find_element_by_id("Password")
        login_btn_elem = driver.find_element_by_id("Login")

        email_elem.send_keys(Config.LAC_USER)
        pw_elem.send_keys(Config.LAC_PW)
        login_btn_elem.click()

    def export_current_contacts(self):
        wait.until(ec.visibility_of_all_elements_located)

        # the export btn is on this page
        browse_url = "https://www.lessannoyingcrm.com/app/Browse"
        driver.get(browse_url)

        time.sleep(6)

        try:
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
                    time.sleep(15)
                logger.info(f"Exported contacts")
        except ElementClickInterceptedException:
            pass
