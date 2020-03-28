import time

from selenium.webdriver import Firefox,Chrome
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

opts = Options()
# opts.headless = True
# driver = Firefox(options=opts, executable_path='/opt/WebDriver/geckodriver')
driver = Chrome(options=opts, executable_path='/opt/WebDriver/geckodriver')


def login():
    driver.get("https://app.convertkit.com/users/login")

    username = driver.find_element_by_id("user_email")
    password = driver.find_element_by_id("user_password")

    username.send_keys("01vendors@gmail.com")
    password.send_keys("Qc4%4P4$")

    submit_btn = "/html/body/div[1]/div/div[2]/div[2]/div/div/div[2]/form/button"
    driver.find_element_by_xpath(submit_btn).click()


def add_single_subscriber(first_name, email, sequences=None):
    wait = WebDriverWait(driver, 10)
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

    em_elems = driver.find_elements_by_tag_name("em")
    sequences_dropdown = em_elems[2]
    sequences_dropdown.click()

    for label in label_elems:
        for seq_name in sequences:
            if seq_name in label.text:
                label.click()

    ##############
    # click save #
    ##############
    add_sub_save_btn = "/html/body/div[1]/div/div[2]/div/div[2]/div/div[1]/div/form/button"  # TODO use relative xpath
    driver.find_element_by_xpath(add_sub_save_btn).click()

    time.sleep(10)


if __name__ == "__main__":
    login()
    sequences = ["Monthly Deals", "Survey Request"]
    add_single_subscriber(first_name="Aatto2", email="aatto@chewy.com", sequences=sequences)

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
