import os

from app import util
from app.constants import Con


class Config:
    CONFIG_PATH = "/Users/ty/src/github/sync-squirrel/config.dev.yaml"
    CONFIG_DATA = util.get_config_data_yaml(CONFIG_PATH)

    ######
    # OS #
    ######
    DOWNLOADS_DIR = util.get_config_value_yaml(CONFIG_DATA, "app.downloads_dir")

    ##############
    # ConvertKit #
    ##############
    CONVERT_USER = util.get_config_value_yaml(CONFIG_DATA, "convertkit.username")
    CONVERT_PW = util.get_config_value_yaml(CONFIG_DATA, "convertkit.password")

    raw_seq = util.get_config_value_yaml(CONFIG_DATA, "convertkit.sequences")
    CONVERT_SEQ = []
    CONVERT_SEQ.append(raw_seq)

    ##########
    # Acuity #
    ##########
    ACUITY_USER = util.get_config_value_yaml(CONFIG_DATA, "acuity.username")
    ACUITY_PW = util.get_config_value_yaml(CONFIG_DATA, "acuity.password")


    #####################
    # Less Annoying CRM #
    #####################
    LAC_API_USER_CODE = util.get_config_value_yaml(CONFIG_DATA, "less_annoying_crm.api_user_code")
    LAC_API_TOKEN = util.get_config_value_yaml(CONFIG_DATA, "less_annoying_crm.api_token")
    LAC_USER = util.get_config_value_yaml(CONFIG_DATA, "less_annoying_crm.username")
    LAC_PW = util.get_config_value_yaml(CONFIG_DATA, "less_annoying_crm.password")

    LAC_CURR_PATH = os.path.join(DOWNLOADS_DIR, Con.LAC_CURR_FILE)

    LAC_PREV_PATH = os.path.join(DOWNLOADS_DIR, Con.LAC_HIST_USERS_FILE)
