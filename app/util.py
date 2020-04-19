import os
import sys
import logging
from functools import reduce
from pathlib import Path
from datetime import datetime

from app.constants import Con

logger = logging.getLogger()  # Note: requires project in calling method to have a logger initialized


def all_files_under(path, ext=None):
    """Iterates through all files that are under the given path."""
    for cur_path, dirnames, filenames in os.walk(path):
        for filename in filenames:
            if ext in filename:
                yield os.path.join(cur_path, filename)


def create_logger(log_level, log_file_path):
    """
    Creates log handler for stdout and log file using the provided logging level and log file path,
    creating the logs parent directory if needed

    :param log_level: absolute path to the log file (e.g. C:\\Users\\tyler.hitzeman\\app\\logs\\app.log)
    :param log_file_path:  name of logging level (e.g. "info", "debug"). See get_logging_level() comments for more info
    """
    create_logs_dir_if_needed(log_file_path=log_file_path)

    print(f"Creating logger with level '{log_level}' and log file at '{log_file_path}' ...")

    try:
        logging.basicConfig(
            format='%(asctime)s: %(levelname)s: %(name)s: %(message)s',
            handlers=[
                logging.FileHandler(filename=log_file_path),
                logging.StreamHandler(stream=sys.stdout)
            ])

        # set level after instantiating
        this_level = get_logging_level(level=log_level)
        logging.getLogger().setLevel(level=this_level)

    except FileNotFoundError as fe:
        print(f"FileNotFoundError while trying to setup logger. Make sure the parent of {log_file_path} exists."
              f"\n\tFull error: {fe}")

    except Exception as e:
        print(f"{type(e): {e}}")


def create_logs_dir_if_needed(log_file_path):
    logs_parent_dir = Path(log_file_path).parent

    if not os.path.exists(logs_parent_dir):
        try:
            os.makedirs(logs_parent_dir, exist_ok=True)
            print(f"Created {logs_parent_dir} directory")
        except OSError:
            print(f"OSError while trying to create {logs_parent_dir}. Make sure path is valid.")
        except Exception as e:
            print(f"{type(e): {e}}")


def get_all_text_from_html_tag(tag):
    from app import driver  # local import to avoid circular imports on startup
    all_text = []

    all_elems = driver.find_elements_by_tag_name(tag)

    for elem in all_elems:
        all_text.append(elem.text)
    return all_text


def get_config_data_yaml(config_file_path):
    """
    Retrieve full config data from YAML file
    Usage:
        CONFIG_DATA = get_config_data_yaml(config_file_path=CONFIG_NAME)

    :param config_file_path: a path-like object giving the pathname (absolute or relative to the current working
    directory) of the file to be opened or an integer file descriptor of the file to be wrapped. (If a file
    descriptor is given, it is closed when the returned I/O object is closed, unless closefd is set to False.)
    :return: All data from config
    """
    # local import to prevent projects that don't use yaml config to have to install pyyaml
    try:
        # local import to prevent projects that don't use yaml config to have to install pyyaml
        from yaml import load, FullLoader

        with open(config_file_path) as f:
            data = load(f, Loader=FullLoader)
            return data

    except ModuleNotFoundError as me:
        logger.exception(f"PyYaml not installed in your project's virtualenv\nRun `pip install pyyaml` and try again"
                         f"\n\n{me}")

    except FileNotFoundError as fe:
        logger.error(f"FileNotFoundError while looking for config at {config_file_path} \n{fe}")

    except Exception as e:
        print(f"{repr(e)}:\n{e}\nUnable to continue without valid configuration in {config_file_path} file")
        sys.exit()


def get_config_value_yaml(config_data, key, default=None):
    """
    Retrieves value from a YAML config, allowing for default value to be set if key not present
    Usage:
        CONFIG_DATA = get_config_data_yaml(config_file_path=CONFIG_NAME)
        APACHE_DIR_NAME = get_config_value_yaml(CONFIG_DATA, key="apache.parent_folder_name", default="Apache24")
    :param config_data: All data from config
    :param key: The config key to search for
    :param default: default value to return if key is not found
    :return: config value that corresponds to the provided key
    """
    val = reduce(lambda d, k: d.get(k, default) if isinstance(d, dict) else default, key.split("."), config_data)

    # extra check handles when nested child value is None
    if val is None:
        if default:
            return default
        else:
            raise KeyError(f"Required config key '{key}' is None. Provide value in config or set a default")

    return val


def get_logging_level(level):
    """
    Converts user-defined string from config file to a logging level.
    Defaults to logging.INFO if KeyError occurs.
    Usage example:
        app.py          CONFIG = utils.get_config_file()                        # get config file
        app.py:         level = utils.get_config(CONFIG)['logging_level']       # read level from config
        Settings.py:    LOGGING_LEVEL = utils.get_logging_level(level=level)    # call this method to get properly typed level
        app.py:         logging.getLogger().setLevel(Settings.LOGGING_LEVEL)    # set base logger's level (do this
                                                                                    after logger instantiation)

    :param level: string from a config file (e.g. 'INFO' or 'info'
    :return: logging.LEVEL that the logging library can discern
    """
    level = level.lower()
    if level == "":
        level = "info"

    logging_level = ""
    try:
        if level == "critical":
            logging_level = logging.CRITICAL
        elif level == "error":
            logging_level = logging.ERROR
        elif level == "warning":
            logging_level = logging.WARNING
        elif level == "info":
            logging_level = logging.INFO
        elif level == "debug":
            logging_level = logging.DEBUG
    except KeyError:
        logging_level = logging.INFO

    return logging_level


def get_xls_path(search_dir):
    curr_xls_files = []

    for file in os.listdir(search_dir):
        if file.endswith(".xls"):
            file_path = os.path.join(search_dir, file)
            curr_xls_files.append(file_path)

    if len(curr_xls_files) > 1:
        warn = f"More than one .xls file in {search_dir}. Deleting all but newest"
        logger.warning(warn)
        newest_xls_path = max(all_files_under(path=search_dir, ext="xls"), key=os.path.getmtime)
        # newest_xls = ntpath.basename(newest_xls_path)
        remove_all_but_newest_file_in_dir(search_dir=search_dir, ext="xls")
        return newest_xls_path

    else:
        xls_name = curr_xls_files[0]
        return xls_name


def remove_all_but_newest_file_in_dir(search_dir, ext=None):
    matching_files = []
    for file in os.listdir(search_dir):
        if file.endswith(f".{ext}"):
            file_path = os.path.join(search_dir, file)
            matching_files.append(file_path)

    if len(matching_files) > 1:
        logger.info("Deleting all but most recent matching file ...")
        newest_xls = max(all_files_under(path=search_dir, ext="xls"), key=os.path.getmtime)

        for xls in matching_files:
            if xls != newest_xls:
                xls_path = os.path.join(search_dir, xls)
                print(f"removing {xls_path} ...")
                os.remove(xls)


def write_to_changelog(msg):
    logger.debug(f"Writing to change log: {msg}")
    now = datetime.now()
    timestamp = now.strftime("%y-%m-%d %H:%M")

    with open(Con.CHANGELOG, "a+") as f:
        f.write(f"\n{timestamp}  {msg}")
