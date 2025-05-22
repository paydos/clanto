"""Module in charge of creating dummy files for quick demo of Clanto"""

import os
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
