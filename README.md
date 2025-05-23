# Clanto: A Client Data Anonymisation Tool

Clanto is a solution designed to assist Machine Learning Engineers and data professionals in securely and compliantly reusing sensitive databases/datasets. By enabling quick and convenient anonymisation of data from diverse sources, Clanto accelerates the development of new use cases, demos, and MVPs while strictly adhering to privacy regulations.

Clanto has an implementation of Format-Preserving Encryption (FPE). This feature ensures that anonymised data retains its original format, allowing it to be "plug-and-play" with existing data pipelines and Machine Learning models without requiring extensive re-engineering.

## Installation

Currently, Clanto can be installed directly from its GitHub repository:
```bash
pip install git+https://github.com/paydos/clanto.git
```

## Usage

Clanto has been designed to be used as a CLI tool, with support as a Python module if desired to be included in a solution.

This tool has an early implementation of Format-Preserving Encryption (FPE) to avoid altering data in a way that stops it from being plug-and-play.

### Command Line Interface

Clanto can be used as a command-line tool with the following arguments:

*   **`input_dir`** (positional argument):
    *   Specifies the directory containing files or a database to be anonymised.
*   **`-o`, `--output-dir`**:
    *   The directory to save the anonymised files and mapping.
    *   _Default_: `clanto_output`
*   **`-m`, `--method`**:
    *   Selects the anonymisation algorithm. Future versions will support custom words/characters and additional methods.
    *   _Choices_: `'random_chars'` (default) or `'random_words'`.
*   **`-t`, `--type`**:
    *   Indicates the input data type. Currently, only ``file`` is supported.
    *   _Choices_: `'file'` (default) or `'db'`.
*   **`--create-dummy`**:
    *   Description: A flag to generate dummy input files in the specified input_dir. Ideal for quickly demonstrating Clanto's capabilities.

**Examples:**

```bash
# Run Clanto's quick demo in the 'demo_data' directory
clanto input_data --create-dummy

# Anonymise files in 'input_directory' using random characters, saving output to 'output_directory'
clanto input_directory --o output_directory -m random_chars -t file

# Anonymise a database in 'db_directory' using random words, saving output to the default directory
clanto db_directory -m random_words -t db
```

## Roadmap
    [ ] Support for databases (local files) 
    [ ] Support for external databases
    [ ] Word anonymisation customisation
    [ ] LLM Support to tailor Clanto's anonymisation method to a new use-case
    [ ]  Differential modelling privacy (for continuos data & time-series)
    [ ] Data Synthesis with MLP
    [ ] Extend Format-Preserving Encryption (FPE).
    [ ] Support for Neo4j and NoSQL databases
    [ ] API support
    [ ] HIPAA & GDPR Compliant