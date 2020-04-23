import os

from app import util
from app.constants import Con


def get_config_file_name():
    cwd = os.getcwd()
    reg_config = "config.yaml"
    dev_config = "config.dev.yaml"
    reg_config_path = os.path.join(cwd, reg_config)
    dev_config_path = os.path.join(cwd, dev_config)

    if os.path.isfile(dev_config_path):
        return dev_config
    elif os.path.isfile(reg_config_path):
        return reg_config
    else:
        return "No config file found"


class Config:
    CONFIG_PATH = get_config_file_name()
    CONFIG_DATA = util.get_config_data_yaml(CONFIG_PATH)

    ######
    # OS #
    ######
    DOWNLOADS_DIR = util.get_config_value_yaml(CONFIG_DATA, "app.downloads_dir")
    WEBDRIVER_PATH = util.get_config_value_yaml(CONFIG_DATA, "app.webdriver_path")
    WEBDRIVER_HEADLESS = util.get_config_value_yaml(CONFIG_DATA, "app.webdriver_headless")

    ##############
    # ConvertKit #
    ##############
    CONVERT_USER = util.get_config_value_yaml(CONFIG_DATA, "convertkit.username")
    CONVERT_PW = util.get_config_value_yaml(CONFIG_DATA, "convertkit.password")
    CONVERT_API_SECRET = util.get_config_value_yaml(CONFIG_DATA, "convertkit.api_secret")

    raw_seq = util.get_config_value_yaml(CONFIG_DATA, "convertkit.sequences")
    CONVERT_SEQ = []
    CONVERT_SEQ.append(raw_seq)

    CONVERT_PREV_USERS_PATH = os.path.join(DOWNLOADS_DIR, Con.CK_HIST_FILE)
    CONVERT_SLEEP_SHORT = util.get_config_value_yaml(CONFIG_DATA, "convertkit.sleep_short")
    CONVERT_SLEEP_MED = util.get_config_value_yaml(CONFIG_DATA, "convertkit.sleep_med")
    CONVERT_SLEEP_LONG = util.get_config_value_yaml(CONFIG_DATA, "convertkit.sleep_long")

    ##########
    # Acuity #
    ##########
    ACUITY_USER = util.get_config_value_yaml(CONFIG_DATA, "acuity.username")
    ACUITY_PW = util.get_config_value_yaml(CONFIG_DATA, "acuity.password")
    ACUITY_CURR_FILE_PATH = os.path.join(DOWNLOADS_DIR, Con.ACUITY_CURR_FILE)
    ACUITY_HIST_FILE_PATH = os.path.join(DOWNLOADS_DIR, Con.ACUITY_HIST_FILE)
    ACUITY_EXPORT_WAIT_TIME_SEC = util.get_config_value_yaml(CONFIG_DATA, "acuity.export_wait_time_s")

    #####################
    # Less Annoying CRM #
    #####################
    LAC_API_USER_CODE = util.get_config_value_yaml(CONFIG_DATA, "less_annoying_crm.api_user_code")
    LAC_API_TOKEN = util.get_config_value_yaml(CONFIG_DATA, "less_annoying_crm.api_token")
    LAC_USER = util.get_config_value_yaml(CONFIG_DATA, "less_annoying_crm.username")
    LAC_PW = util.get_config_value_yaml(CONFIG_DATA, "less_annoying_crm.password")
    LAC_NEW_USER_GROUP_NAME = util.get_config_value_yaml(CONFIG_DATA, "less_annoying_crm.new_user_group_names")

    LAC_CURR_PATH = os.path.join(DOWNLOADS_DIR, Con.LAC_CURR_FILE)

    LAC_PREV_PATH = os.path.join(DOWNLOADS_DIR, Con.LAC_HIST_USERS_FILE)
    LAC_EXPORT_WAIT_TIME_SEC = util.get_config_value_yaml(CONFIG_DATA, "less_annoying_crm.export_wait_time_s")
    LAC_EXPORT_WAIT_TIME_SEC_SHORT = util.get_config_value_yaml(CONFIG_DATA,
                                                                "less_annoying_crm.export_wait_time_s_short")
