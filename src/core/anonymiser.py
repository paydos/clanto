from tqdm import tqdm
import pandas as pd
import os
from ..utils import (
    generate_random_string,
    generate_random_word_string,
    is_identifiable_string,
    anonymise_email,
    anonymise_phone,
)
from ..discovery.lookup import (
    DatabaseManager,
    FileManager,
    RawFile,
    ClantoFile,
    MappingTemplateManager,
)
from ..config import DEFAULT_ANONYMISATION_OPTIONS
from configparser import ConfigParser

import re


class Anonymiser:
    def __init__(
        self,
        manager: DatabaseManager | FileManager,
        output_dir: str = "clanto_output",
        anonymisation_method: str = "random_chars",
        make_mapping: bool = False,
        cfg: ConfigParser = None,
    ) -> None:
        """
        Initialises the Anonymiser.

        Args:
            output_dir (str): Directory to save the anonymised files and mapping.
            anonymisation_method (str): 'random_chars' for random character strings,
                                        'random_words' for strings based on random words.
            make_mapping (bool): Boolean to create or not the mapping template for custom use
        """
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.cfg = cfg

        self.mapping: dict = {}
        """Dictionary containing the mapping of anonymised data"""

        self.reverse_mapping: dict = {}
        """Dictionary containing the mapping of anonymised data, reversed for collision checking"""

        self.manager = manager
        """manager containing the file(s) to be anonymised """

        self.anonymisation_method = anonymisation_method
        self.options = DEFAULT_ANONYMISATION_OPTIONS.copy()

        self.mapping_manager = MappingTemplateManager(output_dir)

    def _get_anonymised_value(self, original_value: str) -> str:
        """
        Gets an anonymised value for a given original value.
        Ensures coherence by reusing existing anonymised values.
        Handles potential collisions for new anonymised values.

        :param original_value: Self explanatory
        :type original_value: str
        :raises ValueError: If arg parsed does not match one of the available methods
        :return: The new anonymised value
        :rtype: str
        """
        if original_value in self.mapping:
            return self.mapping[original_value]

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if re.search(email_pattern, original_value):
            new_value = anonymise_email(original_value)
            while new_value in self.reverse_mapping:
                new_value = anonymise_email(original_value)
            self.mapping[original_value] = new_value
            self.reverse_mapping[new_value] = original_value
            return new_value

        phone_pattern = r"^[\d\s\-\(\)\+]*\d[\d\s\-\(\)\+]*$"
        if re.search(phone_pattern, original_value):
            new_value = anonymise_phone(original_value)
            while new_value in self.reverse_mapping:
                new_value = anonymise_phone(original_value)
            self.mapping[original_value] = new_value
            self.reverse_mapping[new_value] = original_value
            return new_value

        new_value = None
        while new_value is None or new_value in self.reverse_mapping:
            if self.anonymisation_method == "random_chars":
                new_value = generate_random_string(
                    length=self.options["random_length"], prefix=self.options["prefix"]
                )
            elif self.anonymisation_method == "random_words":
                new_value = generate_random_word_string(prefix=self.options["prefix"])
            else:
                raise ValueError(
                    f"Unknown anonymisation method: {self.anonymisation_method}"
                )

        self.mapping[original_value] = new_value
        self.reverse_mapping[new_value] = original_value
        return new_value

    def __save(self) -> None:
        self.manager.save_files()
        self.mapping_manager.save_files()

    def anonymise_file(self, f: RawFile) -> None:
        """
        Reads a single CSV or XLSX file, anonymises it, and saves the output.

        :param filepath: RawFile path
        :type filepath: str
        """

        anonymised_df = f.df.copy()

        anonymised_df = anonymised_df.map(
            lambda value: (
                self._get_anonymised_value(value)
                if is_identifiable_string(value)
                else value
            )
        )

        output_filename = f"anonymised_{f.filename}"

        self.manager.add_clanto_file(
            ClantoFile(
                path=os.path.join(self.output_dir, output_filename), df=anonymised_df
            )
        )

    def anonymise_files(self):
        """
        Anonymises a list of CSV or XLSX files.

        :param filepaths: List of paths
        """

        if not self.manager.raw_loaded:
            print("No supported files found for anonymisation.")
            return
        from tqdm import tqdm

        tqdm_iterator = tqdm(self.manager.raw_loaded.items(), desc="Anonymising files")
        for _, fobj in tqdm_iterator:
            tqdm_iterator.set_description(f"Anonymising file: {fobj.filename}")
            self.anonymise_file(fobj)

        mapping_df = pd.DataFrame(
            self.mapping.items(), columns=["Original Value", "Anonymised Value"]
        )
        mapping_filepath = os.path.join(self.output_dir, "anonymisation_mapping.csv")

        self.manager.add_clanto_file(ClantoFile(mapping_filepath, mapping_df))

        self.__save()

    def gen_map_template(self):
        """Generate a .json mapping template for the user to fill in."""
        import json

        if self.cfg and self.cfg.has_section("mapping_template_rules"):
            if self.cfg.has_option("mapping_template_rules", "non_identifiable"):
                _regex_rules = self.cfg.getlist(
                    "mapping_template_rules", "non_identifiable"
                )
                if not isinstance(_regex_rules, list):
                    raise TypeError(
                        f"Regex rules for mapping template must be list[str], not {type(_regex_rules).__name__}"
                    )

        self.mapping_template: dict = {}
        """A mapping template for the user to fill in later."""
        if not self.manager.raw_loaded:
            print("No supported files found to generate the mapping template.")
            return

        for f in self.manager.raw_loaded.values():
            df = f.df
            for column in df.columns:
                for value in df[column].unique():
                    if is_identifiable_string(value, _regex_rules):
                        self.mapping_template[value] = ""
        self.mapping_manager.map_template = self.mapping_template
        self.__save()
