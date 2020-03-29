import sys

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
