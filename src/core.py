from typing import Iterable
import pandas as pd
import os
from .utils import (
    generate_random_string,
    generate_random_word_string,
    is_identifiable_string,
    anonymise_email,
    anonymise_phone,
)
from .config import DEFAULT_ANONYMISATION_OPTIONS
import re


class Anonymiser:
    def __init__(
        self,
        output_dir: str = "clanto_output",
        anonymisation_method: str = "random_chars",
    ) -> None:
        """
        Initialises the Anonymiser.

        Args:
            output_dir (str): Directory to save the anonymised files and mapping.
            anonymisation_method (str): 'random_chars' for random character strings,
                                        'random_words' for strings based on random words.
        """
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

        self.mapping: dict = {}
        """Dictionary containing the mapping of anonymised data"""

        self.reverse_mapping: dict = {}
        """Dictionary containing the mapping of anonymised data, reversed for collision checking"""

        self.anonymisation_method = anonymisation_method
        self.options = DEFAULT_ANONYMISATION_OPTIONS.copy()

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

    def anonymise_file(self, filepath: str) -> None:
        """
        Reads a single CSV or XLSX file, anonymises it, and saves the output.

        :param filepath: File path
        :type filepath: str
        """
        print(f"\rAnonymising file: {filepath}", end="", flush=True)
        file_extension = os.path.splitext(filepath)[1].lower()
        df = None

        if file_extension == ".csv":
            df = pd.read_csv(filepath)
        elif file_extension in [".xlsx", ".xls"]:
            df = pd.read_excel(filepath)
        else:
            print(f"\nSkipping unsupported file type: {filepath}")
            return

        anonymised_df = df.copy()
        total_columns = len(anonymised_df.columns)
        total_rows = len(anonymised_df)

        for col_idx, column in enumerate(anonymised_df.columns):
            print(
                f"\rProcessing file: {os.path.basename(filepath)} - Column {col_idx + 1}/{total_columns}",
                end="",
                flush=True,
            )
            for i, value in enumerate(anonymised_df[column]):
                if is_identifiable_string(value):
                    anonymised_df.at[i, column] = self._get_anonymised_value(value)

        output_filename = f"anonymised_{os.path.basename(filepath)}"
        output_filepath = os.path.join(self.output_dir, output_filename)

        if file_extension == ".csv":
            anonymised_df.to_csv(output_filepath, index=False)
        elif file_extension in [".xlsx", ".xls"]:
            anonymised_df.to_excel(output_filepath, index=False)

        print(f"\nAnonymised file saved to: {output_filepath}")

    def anonymise_files(self, filepaths: Iterable[str]):
        """
        Anonymises a list of CSV or XLSX files.

        :param filepaths: List of paths
        :type filepaths: Iterable[str]
        """
        if not filepaths:
            print("No supported files found for anonymisation.")
            return

        total_files = len(filepaths)
        for file_idx, filepath in enumerate(filepaths):
            print(f"\rProcessing file {file_idx + 1}/{total_files}", end="", flush=True)
            self.anonymise_file(filepath)

        mapping_df = pd.DataFrame(
            self.mapping.items(), columns=["Original Value", "Anonymised Value"]
        )
        mapping_filepath = os.path.join(self.output_dir, "anonymisation_mapping.csv")
        mapping_df.to_csv(mapping_filepath, index=False)
        print(f"\nAnonymisation mapping saved to: {mapping_filepath}")
