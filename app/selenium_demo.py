import time

from selenium.webdriver import Chrome
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from app import logger
from app.config import Config

opts = Options()
# opts.headless = True
# driver = Firefox(options=opts, executable_path='/opt/WebDriver/geckodriver')
driver = Chrome(options=opts, executable_path='/opt/WebDriver/geckodriver')
wait = WebDriverWait(driver, 10)


def login(username, password):
    logger.info("Logging in ...")
    driver.get("https://app.convertkit.com/users/login")

    username_elem = driver.find_element_by_id("user_email")
    password_elem = driver.find_element_by_id("user_password")

    username_elem.send_keys(username)
    password_elem.send_keys(password)

    submit_btn = "/html/body/div[1]/div/div[2]/div[2]/div/div/div[2]/form/button"
    driver.find_element_by_xpath(submit_btn).click()


def add_single_subscriber(first_name, email, sequences=None):
    logger.info("adding subscriber")
    wait.until(ec.visibility_of_all_elements_located)

    add_subs_btn = driver.find_element_by_css_selector(".break > div:nth-child(1) > a:nth-child(1)")
    add_subs_btn.click()

    singl_sub_btn = driver.find_element_by_css_selector("a.btn--step:nth-child(1)")
    singl_sub_btn.click()

    # wait
    wait.until(ec.visibility_of_all_elements_located)

    ########################
    # enter name and email #
    ########################

    first_name_element = driver.find_element_by_id("first-name")
    email_element = driver.find_element_by_id("email")

    #####################
    # add subscriber(s) #
    #####################

    span_elem = driver.find_elements_by_tag_name("span")
    span_text = []
    for span in span_elem:
        span_text.append(span.text)
    label_elems = driver.find_elements_by_tag_name("label")

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
    for label in label_elems:
        for seq_name in sequences:
            if seq_name in label.text:
                label.click()
                break

    ##############
    # click save #
    ##############
    add_sub_save_btn = "/html/body/div[1]/div/div[2]/div/div[2]/div/div[1]/div/form/button"  # TODO use relative xpath
    driver.find_element_by_xpath(add_sub_save_btn).click()

    time.sleep(10)


if __name__ == "__main__":
    new_user_first_name = "Stan"
    new_user_email = "foo@bar.com"

    login(username=Config.CONVERT_USER, password=Config.CONVERT_PW)
    add_single_subscriber(first_name=new_user_email, email=new_user_email, sequences=Config.CONVERT_SEQ)

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


"""
