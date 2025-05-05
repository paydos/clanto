"""Lookup for files and databases for Clanto"""

from .utils import _file_discovery, load_non_db, save_non_db

from ..config import DATABASE_SUPPORT, FILE_SUPPORT
from ..clanto_cfg import __find_cfg, _ROOTDIR, _CFG_PATH, _CLANTO_JSON
from ..core.base_reader import ClantoFileManager, RawFile, ClantoFile
from ..objects.template import MappingTemplate
from .utils import _file_discovery, load_clason

import json
import os


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


class MappingTemplateManager(ClantoFileManager):
    def __init__(self, output_path: str) -> None:

        super().__init__(root_path="", output_path=output_path)

    def _load(self) -> list[str]:
        """
        Abstract method implementation for MappingTemplateManager.
        This manager's primary role is to save mapping templates, not to discover
        or load files in the same manner as other ClantoFileManagers.
        Returns an empty list as there are no "sources" to load in this context.
        """
        files = _file_discovery(_ROOTDIR, _CLANTO_JSON)

        for f in files:
            if "custom_rules" in f:
                self.custom_sub = load_clason(f)
            elif "mapping_template" in f:
                self.map_template = load_clason(f)

    def save_files(self) -> None:
        """
        Saves the provided mapping template dictionary to a JSON file
        in the specified output directory.

        Args:
            file (dict): The dictionary representing the mapping template to save.
        """

        with open(self.map_template.path, "w", encoding="utf-8") as f:
            json.dump(self.map_template.file, f, indent=4)

    @property
    def map_template(self):
        return self._map_template

    @map_template.setter
    def map_template(self, value: dict) -> MappingTemplate:
        if not isinstance(value, dict):
            raise TypeError(
                f"Expected 'dict', but got '{type(value).__name__}' instead."
            )
        __path = os.path.join(_CFG_PATH or _ROOTDIR, "mapping_template.clason")
        self._map_template = MappingTemplate(file=value, path=__path)

    @property
    def custom_sub(self):
        return self._custom_sub

    @custom_sub.setter
    def custom_sub(self, value: dict) -> MappingTemplate:
        if not isinstance(value, dict):
            raise TypeError(
                f"Expected 'dict', but got '{type(value).__name__}' instead."
            )
        __path = os.path.join(_CFG_PATH or _ROOTDIR, "substitution_rules.clason")
        self._custom_sub = MappingTemplate(file=value, path=__path)
