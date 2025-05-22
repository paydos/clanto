"""Lookup for files and databases for Clanto"""

from .utils import _file_discovery, load_non_db, save_non_db

from ..config import DATABASE_SUPPORT, FILE_SUPPORT
from ..core.base_reader import ClantoFileManager, RawFile, ClantoFile

import pandas as pd


class DatabaseManager(ClantoFileManager):
    __SUPPORTED_FILES = DATABASE_SUPPORT

    def __init__(self, root_path: str) -> None:
        self._db_path = _file_discovery(root_path, self.__SUPPORTED_FILES)
        super().__init__()


class FileManager(ClantoFileManager):
    __SUPPORTED_FILES = FILE_SUPPORT

    def __init__(self, root_path: str, output_dir: str = None) -> None:

        super().__init__(root_path, output_dir)

        self.__file_paths = _file_discovery(root_path, self.__SUPPORTED_FILES)
        if not isinstance(self.__file_paths, list):
            self.__file_paths = [self.__file_paths]

        self.raw_loaded: dict[str, RawFile] = {}
        self.clantod_files: list[ClantoFile] = []
        self.clanto_mapping: ClantoFile = None
        self._load()

    def _load(self) -> None:
        """Load files into memory"""

        for file in self.__file_paths:
            f = load_non_db(file)
            self.raw_loaded[f.filename] = f

    def add_clanto_file(self, clanto: ClantoFile):
        """
        Adds a ClantoFile object to the list of processed files.

        Args:
            clanto (ClantoFile): The ClantoFile object to add.

        Raises:
            TypeError: If the provided object is not a ClantoFile instance.
        """
        if not isinstance(clanto, ClantoFile):
            raise TypeError(
                f"Expected 'ClantoFile', but received '{type(clanto).__name__}'"
            )

        self.clantod_files.append(clanto)

    def save_files(
        self,
    ) -> None:
        """Saves all processed ClantoFiles and the mapping file."""
        for f in self.clantod_files:
            save_non_db(f)
