from app import util


class Config:
    CONFIG_PATH = "/Users/ty/src/github/sync-squirrel/config.dev.yaml"
    CONFIG_DATA = util.get_config_data_yaml(CONFIG_PATH)

    ##########
    # Chrome #
    ##########
    DOWNLOADS_DIR = "/Users/ty/Downloads"

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
    ARCHIVE_CSV_NAME = "list_users_previous.csv"
