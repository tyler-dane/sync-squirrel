import os

from app import util
from app.constants import Con


class Config:
    CONFIG_PATH = "config.yaml"
    CONFIG_DATA = util.get_config_data_yaml(CONFIG_PATH)

    ######
    # OS #
    ######
    DOWNLOADS_DIR = util.get_config_value_yaml(CONFIG_DATA, "app.downloads_dir")
    WEBDRIVER_PATH = util.get_config_value_yaml(CONFIG_DATA, "app.webdriver_path")

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

    ##########
    # Acuity #
    ##########
    ACUITY_USER = util.get_config_value_yaml(CONFIG_DATA, "acuity.username")
    ACUITY_PW = util.get_config_value_yaml(CONFIG_DATA, "acuity.password")
    ACUITY_CURR_FILE_PATH = os.path.join(DOWNLOADS_DIR, Con.ACUITY_CURR_FILE)
    ACUITY_HIST_FILE_PATH = os.path.join(DOWNLOADS_DIR, Con.ACUITY_HIST_FILE)


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
