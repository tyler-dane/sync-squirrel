SELENIUM NOTES

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

