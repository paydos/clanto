"""Module in charge of finding compatible files"""

from abc import ABC, abstractmethod

import os

import pandas as pd
from dataclasses import dataclass, field
import os


@dataclass
class BaseFile:
    """
    Base class for file representations.
    """

    path: str
    """Path to the file"""
    df: pd.DataFrame
    """Loaded dataframe"""
    filename: str = field(init=False)
    """Filename"""
    ext: str = field(init=False)
    """File extension"""

    def __post_init__(self) -> None:
        """
        Post-initialization to set the filename and extension based on the path.
        """
        if not isinstance(self.path, str):
            raise TypeError("path must be a string")
        if not isinstance(self.df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame")

        self.filename = os.path.basename(self.path)
        self.ext = os.path.splitext(self.path)[1].lower()


@dataclass
class RawFile(BaseFile):
    """
    Represents a single raw file (non-Clanto'd) with its path, filename, extension and loaded DataFrame.
    Inherits from BaseFile.
    """

    ...


@dataclass
class ClantoFile(BaseFile):
    """
    Represents a file that has been Clanto'd.
    Inherits from BaseFile.
    """

    ...


class ClantoFileManager(ABC):

    def __init__(self, root_path: str, output_path: str) -> None:
        """
        Initializes the ClantoFileManager base class.

        Args:
            root_path (str): The root path for discovering files or databases.
            output_path (str): The directory where anonymised files will be saved.
        """
        self.root_path = root_path
        self.output_path = output_path
        self.__ensure_path(self.output_path)

    @staticmethod
    def __ensure_path(path: str) -> None:
        """Ensures the given directory path exists, creating it if necessary."""
        os.makedirs(path, exist_ok=True)

    @abstractmethod
    def _load(self) -> list[str]:
        """
        Abstract method to find data sources (files, tables, etc.).
        Subclasses must implement this method to define how they locate sources.
        Returns a list of identifiers for the found sources (e.g., file paths, table names).
        """
        ...

    @abstractmethod
    def save_files(self) -> None:
        """Abstract method to save files to an output directory"""
        ...
