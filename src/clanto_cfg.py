"""This module is in charge of reading and setting a custom configuration"""

import configparser
from .clanto_exc import MultipleConfigFiles
from .discovery.utils import _file_discovery
from .core.base_reader import BaseFile
import os


__CLANTO_CFG_EXT = "*.clanto"
_ROOTDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def __find_cfg(path: str) -> str | None:
    """Try quick configuration file lookup, if not provided as an argument.

    :param path: Root path
    :type path: str
    :return: The path of the configuration file, if available, otherwise None.
    :rtype: str | None
    """
    cfg_file = _file_discovery(path, __CLANTO_CFG_EXT)

    if isinstance(cfg_file, list):
        raise MultipleConfigFiles
    elif isinstance(cfg_file, str):
        return cfg_file
    else:
        return None


_found_cfg_path = __find_cfg(_ROOTDIR)
_CFG_PATH = os.path.dirname(_found_cfg_path) if _found_cfg_path else None


def _load_cfg(path: str) -> tuple[configparser.ConfigParser, str | None]:
    """Loads the Clanto configuration from a file.

    Searches for a .clanto file in the given path. If found, loads the
    configuration. If multiple files are found, raises MultipleConfigFiles.
    If no file is found, returns an empty ConfigParser object.

    :param path: The root path to search for the config file.
    :type path: str
    :return: A tuple containing:
             - A ConfigParser object containing the configuration.
             - The directory of the configuration file, or None if not found.
    :rtype: tuple[configparser.ConfigParser, str | None]
    """
    cfg_file_path = __find_cfg(path)

    __cfg = configparser.ConfigParser(
        converters={"list": lambda x: [i.strip() for i in x.split(",")]}
    )

    if cfg_file_path:
        __cfg.read(cfg_file_path)
        relative_cfg_path = os.path.relpath(cfg_file_path, path)
        print(f"Configuration file found at relative path: {relative_cfg_path}")

    if cfg_file_path:
        cfg_file_path = os.path.dirname(cfg_file_path)

    return __cfg, cfg_file_path


if __name__ == "__main__":
    file = __find_cfg("C:\\Users\\d.ruiz.blanco\\Documents\\Personal\\Projects\\clanto")

    print(_load_cfg(file))
