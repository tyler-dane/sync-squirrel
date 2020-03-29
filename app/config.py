
from app import util

class Config:
    CONFIG_DATA = util.get_config_data_yaml("config.dev.yaml")

    CONVERT_USER = util.get_config_value_yaml(CONFIG_DATA, "convertkit.username")
    CONVERT_PW = util.get_config_value_yaml(CONFIG_DATA, "convertkit.password")

    raw_seq = util.get_config_value_yaml(CONFIG_DATA, "convertkit.sequences")
    CONVERT_SEQ = []
    CONVERT_SEQ.append(raw_seq)
