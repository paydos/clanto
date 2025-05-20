# Clanto

A Python tool for anonymising sensitive data in CSV and Excel files.

## Installation

```bash
pip install clanto
```

## Usage

### Command Line Interface

```bash
clanto input_data --create-dummy

clanto input_directory --output-dir output_directory --method random_chars
```

### As a Python Module

```python
from anon_module import Anonymiser

# Initialise the anonymiser
anon = Anonymiser(output_dir="output_directory", anonymisation_method="random_chars")

# Anonymise specific files
anon.anonymise_files(["path/to/file1.csv", "path/to/file2.xlsx"])
```

## Features

- Supports CSV and Excel files
- Multiple anonymisation methods (random characters or random words)
- Preserves data relationships across files
- Generates mapping files for reference
- Can create dummy data for testing
