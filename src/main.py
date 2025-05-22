# Anonymiser_module/main.py

import argparse
import os
import glob
from .core.anonymiser import Anonymiser
from .config import FILE_SUPPORT, DATABASE_SUPPORT
from .discovery.lookup import DatabaseManager, FileManager
from .example.dummy_gen import create_dummy_files
import pandas as pd


def main():
    """
    In charge of parsing arguments and running Clanto
    """
    parser = argparse.ArgumentParser(
        description="Anonymise text in CSV and XLSX files."
    )
    parser.add_argument(
        "input_dir", help="Directory containing the CSV/XLSX files to anonymise."
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        help="Directory to save the Anonymised files and mapping.",
        default="clanto_output",
    )
    parser.add_argument(
        "-m",
        "--method",
        help="Anonymisation method: 'random_chars' or 'random_words'.",
        choices=["random_chars", "random_words"],
        default="random_chars",
    )

    parser.add_argument(
        "-t",
        "--type",
        help=f"File extension to look for: 'file' or 'db'.\n Supported extensions in 'file': {FILE_SUPPORT}\nSupported extensions in 'db': {DATABASE_SUPPORT}",
        choices=["file", "db"],
        default="file",
    )
    parser.add_argument(
        "--create-dummy",
        action="store_true",
        help="Create dummy input files in the specified input directory.",
    )

    args = parser.parse_args()

    if args.create_dummy:
        create_dummy_files(args.input_dir)

    input_directory = args.input_dir
    output_directory = args.output_dir
    anonymisation_method = args.method
    file_ext = args.type

    if file_ext == "file":
        fmanager = FileManager(input_directory, output_directory)
    elif file_ext == "db":
        fmanager = DatabaseManager(input_directory, output_directory)

    anon = Anonymiser(
        output_dir=output_directory,
        anonymisation_method=anonymisation_method,
        manager=fmanager,
    )
    anon.anonymise_files()

    print("\nAnonymisation process finished.")


if __name__ == "__main__":
    main()
