from tqdm import tqdm
import pandas as pd
import os
from ..utils import (
    generate_random_string,
    generate_random_word_string,
    is_identifiable_string,
    anonymise_email,
    custom_mapping_replacement,
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

tqdm.pandas()


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
        if anonymisation_method == "custom_mapping":
            self.mapping_manager._load()

    def _get_anonymised_value(self, original_value: str) -> str:
        """
        Gets an anonymised value for a given original value.
        Ensures coherence by reusing existing anonymised values.
        Handles potential collisions for new anonymised values.
        Can identify and replace multiple identifiable entities within a single string.

        :param original_value: The string value to be anonymised.
        :type original_value: str
        :raises ValueError: If an unknown anonymisation method is specified.
        :return: The anonymised value.
        :rtype: str
        """

      
        def _get_anonymised_single_token(
            token: str, token_type: str = "general"
        ) -> str:
            if token in self.mapping:
                return self.mapping[token]

            new_token_value = None
            should_retry_generation = True
            is_first_attempt = True

            while should_retry_generation and (
                new_token_value is None or new_token_value in self.reverse_mapping
            ):
                status_message = (
                    "Generating new value"
                    if is_first_attempt
                    else "Retrying generation"
                )
              

                if self.anonymisation_method == "custom_mapping":
                    new_token_value = custom_mapping_replacement(
                        token, self.mapping_manager
                    )
                    if new_token_value in self.reverse_mapping:
                    
                        should_retry_generation = (
                            False  
                        )
                else:  
                    if token_type == "email":
                        new_token_value = anonymise_email(token)
                    elif token_type == "phone":
                        new_token_value = anonymise_phone(token)
                    elif self.anonymisation_method == "random_chars":
                        new_token_value = generate_random_string(
                            length=self.options["random_length"],
                            prefix=self.options["prefix"],
                        )
                    elif self.anonymisation_method == "random_words":
                        new_token_value = generate_random_word_string(
                            prefix=self.options["prefix"]
                        )
                    else:
                        raise ValueError(
                            f"Unknown anonymisation method: {self.anonymisation_method}"
                        )

                    if new_token_value in self.reverse_mapping:
                        colliding_original = self.reverse_mapping[new_token_value]
                        # print(
                        #     f"  -> Collision detected for '{new_token_value}'. "
                        #     f"It is already mapped to '{colliding_original}'. "
                        #     f"Attempting to generate another value for '{token}'."
                        # )
                        #

                is_first_attempt = False  

            self.mapping[token] = new_token_value
            self.reverse_mapping[new_token_value] = token
            return new_token_value

        # --- Main logic for _get_anonymised_value ---

        if original_value in self.mapping:
            return self.mapping[original_value]

        email_pattern_in_text = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

        phone_pattern_in_text = (
            r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{4}\b"
        )

    
        combined_pattern = re.compile(
            f"(?P<email>{email_pattern_in_text})|(?P<phone>{phone_pattern_in_text})"
        )

        made_replacements = False

        def replacer(match):
            nonlocal made_replacements
            matched_string = match.group(0)
            replaced_value = matched_string 

            if match.group("email"):
                replaced_value = _get_anonymised_single_token(matched_string, "email")
                made_replacements = True
            elif match.group("phone"):
                replaced_value = _get_anonymised_single_token(matched_string, "phone")
                made_replacements = True
            elif match.group("general_word"):
                if is_identifiable_string(matched_string, self._regex_rules):
                    replaced_value = _get_anonymised_single_token(matched_string, "general")
                    made_replacements = True

            return replaced_value

        anonymised_value_with_parts_replaced = combined_pattern.sub(
            replacer, original_value
        )

        if made_replacements:
        
            self.mapping[original_value] = anonymised_value_with_parts_replaced
            self.reverse_mapping[anonymised_value_with_parts_replaced] = original_value
            return anonymised_value_with_parts_replaced
        else:

            final_anonymised_value = _get_anonymised_single_token(
                original_value, "general"
            )
            self.mapping[original_value] = final_anonymised_value
            self.reverse_mapping[final_anonymised_value] = original_value
            return final_anonymised_value

    def __save(self) -> None:
        self.manager.save_files()
        self.mapping_manager.save_files()

    def anonymise_file(self, f: RawFile) -> None:
        """
        Reads a single CSV or XLSX file, anonymises it, and saves the output.

        :param filepath: RawFile path
        :type filepath: str
        """

        tqdm.pandas(desc=f"Anonymising {f.filename}")

        anonymised_df = f.df.copy()

        anonymised_df = anonymised_df.progress_map(
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
        os.system("cls" if os.name == "nt" else "clear")

    def anonymise_files(self):
        """
        Anonymises a list of CSV or XLSX files.

        :param filepaths: List of paths
        """

        if not self.manager.raw_loaded:
            print("No supported files found for anonymisation.")
            return
        for _, fobj in self.manager.raw_loaded.items():
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

        tqdm_iterator = tqdm(
            self.manager.raw_loaded.values(), desc="Creating mapping template"
        )
        for f in tqdm_iterator:
            tqdm_iterator.set_description(f"Scanning {f.filename}")
            df = f.df
            for column in df.columns:
                for value in df[column].unique():
                    if is_identifiable_string(value, _regex_rules):
                        self.mapping_template[value] = ""

        self.mapping_manager.map_template = self.mapping_template
        self.__save()
