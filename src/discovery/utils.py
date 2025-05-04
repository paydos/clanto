"""Utility functions for readers"""

import glob
import os
from ..core.base_reader import RawFile, ClantoFile

import pandas as pd


def _file_discovery(
    root_path: str, supported_files: str | list[str]
) -> str | list[str]:
    """Recursive file lookup

    :param root_path: Base path
    :type root_path: str
    :param supported_files: RawFile extension(s) to allow in search
    :type supported_files: str | list[str]
    :return: RawFile(s) found
    :rtype: str | list[str]
    """
    # Quick checks
    if not isinstance(root_path, str):
        raise TypeError("root_path must be a string")
    if isinstance(supported_files, str):
        patterns_to_search = [supported_files]
    elif isinstance(supported_files, list):
        for p in supported_files:
            if not isinstance(p, str):
                raise TypeError(
                    f"supported_files list must contain only strings, but found element '{p}' of type {type(p).__name__}."
                )
        patterns_to_search = supported_files
    else:
        raise TypeError("supported_files must be a string or a list of strings")

    found_files = []

    for pattern in patterns_to_search:
        # Construct the pattern for recursive search
        full_pattern = os.path.join(root_path, "**", pattern)
        # Use recursive=True to search subdirectories
        found_files.extend(glob.glob(full_pattern, recursive=True))

    if not found_files:
        patterns_str = ", ".join(patterns_to_search)
        raise FileNotFoundError(
            f"No files found matching patterns '{patterns_str}' in directory '{root_path}' or its subdirectories."
        )

    return found_files if len(found_files) > 1 else found_files[0]


def load_non_db(f: str, *args, **kwargs) -> RawFile:
    """
    Loads a non-database supported file into a pandas DataFrame.

    Args:
        f (str): The path to the file.
        *args: Positional arguments to pass to pandas read function.
        **kwargs: Keyword arguments to pass to pandas read function.

    Returns:
        RawFile: RawFile dataclass
    """

    _f_xt = os.path.splitext(f)[1].lower()  # file ext

    if _f_xt == ".csv":
        df = pd.read_csv(f, *args, **kwargs)
    elif _f_xt in [".xlsx", ".xls"]:
        df = pd.read_excel(f, *args, **kwargs)
    else:
        raise ValueError(f"Unsupported file extension: {_f_xt}")
    return RawFile(f, df)


def save_non_db(f: ClantoFile, *args, **kwargs) -> RawFile:
    """
    Loads a non-database supported file into a pandas DataFrame.

    Args:
        f (str): The path to the file.
        *args: Positional arguments to pass to pandas read function.
        **kwargs: Keyword arguments to pass to pandas read function.

    Returns:
        RawFile: RawFile dataclass
    """

    if f.ext == ".csv":
        f.df.to_csv(f.path, index=False)
    elif f.ext in [".xlsx", ".xls"]:
        f.df.to_excel(f.path, index=False)
