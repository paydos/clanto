# Anonymiser_module/main.py

import argparse
import os
import glob
from .core import Anonymiser
import pandas as pd


def create_dummy_files(directory: str = "input_data") -> None:
    """Create dummy files to test how Clanto works

    :param directory: Folder on which data will be saved, defaults to "input_data"
    :type directory: str, optional
    """
    os.makedirs(directory, exist_ok=True)

    data1 = {
        "Name": ["Alice Smith", "Bob Johnson", "Charlie Brown", "Alice Smith"],
        "Email": [
            "alice@example.com",
            "bob@domain.com",
            "charlie@mail.org",
            "alice@example.com",
        ],
        "Age": [30, 25, 35, 30],
        "City": ["New York", "Los Angeles", "Chicago", "New York"],
        "DateJoined": ["2023-01-15", "2022-11-20", "2024-03-10", "2023-01-15"],
    }
    df1 = pd.DataFrame(data1)
    df1.to_csv(os.path.join(directory, "customers.csv"), index=False)

    data2 = {
        "Product": ["Laptop", "Mouse", "Keyboard", "Monitor"],
        "CustomerEmail": [
            "bob@domain.com",
            "charlie@mail.org",
            "alice@example.com",
            "bob@domain.com",
        ],
        "Price": [1200.50, 25.00, 75.99, 300.00],
        "OrderID": ["ORD001", "ORD002", "ORD003", "ORD004"],
    }
    df2 = pd.DataFrame(data2)
    df2.to_csv(os.path.join(directory, "orders.csv"), index=False)

    data3 = {
        "EmployeeID": ["EMP001", "EMP002", "EMP003"],
        "FullName": ["David Lee", "Eve White", "Frank Green"],
        "Department": ["HR", "Engineering", "Sales"],
        "HireDate": ["2021-05-01", "2020-09-10", "2022-02-28"],
    }
    df3 = pd.DataFrame(data3)
    df3.to_excel(os.path.join(directory, "employees.xlsx"), index=False)

    print(f"Sample files created in '{directory}' directory.")


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

    supported_files = []
    for ext in ["*.csv", "*.xlsx", "*.xls"]:
        supported_files.extend(glob.glob(os.path.join(input_directory, ext)))

    if not supported_files:
        print(f"No supported CSV or XLSX files found in '{input_directory}'.")
        return

    print(f"Found {len(supported_files)} supported files in '{input_directory}'.")

    anon = Anonymiser(
        output_dir=output_directory, anonymisation_method=anonymisation_method
    )
    anon.anonymise_files(supported_files)

    print("\nAnonymisation process finished.")


if __name__ == "__main__":
    main()
