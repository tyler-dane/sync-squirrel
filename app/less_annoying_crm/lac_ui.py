from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as ec
from app import logger, driver, wait
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
        logger.info("Sleeping before going to LAC endpoint ...")
        time.sleep(Config.LAC_EXPORT_WAIT_TIME_SEC_SHORT)
        wait.until(ec.visibility_of_all_elements_located)

        # the export btn is on this page
        browse_url = "https://www.lessannoyingcrm.com/app/Browse"
        driver.get(browse_url)

        logger.info(f"Sleeping before trying to export ...")
        time.sleep(Config.LAC_EXPORT_WAIT_TIME_SEC_SHORT)
        successfully_exported = False

        try:
            # find the 'Export' btn/link
            all_a_elems = driver.find_elements_by_tag_name("a")
            for a in all_a_elems:
                if "Export" in a.text:
                    logger.info("Found LAC's export button")
                    actions = ActionChains(driver)
                    actions.move_to_element(a)  # must hover over before click works
                    actions.click()
                    actions.perform()

                    logger.info("Clicking export button ...")
                    a.click()
                    logger.info("Sleeping to let export finish ...")
                    time.sleep(Config.LAC_EXPORT_WAIT_TIME_SEC)
                    successfully_exported = True
                    logger.info(f"Exported LAC contacts")
            if successfully_exported is False:
                logger.error("Did not export LAC contacts :(")
        except ElementClickInterceptedException:
            pass
