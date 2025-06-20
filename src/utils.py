import pandas as pd
import random
import re
from datetime import datetime
from typing import Any
from .config import RANDOM_CHARS, RANDOM_WORDS
from .discovery.lookup import MappingTemplateManager


def is_number(value: float | int | str) -> bool:
    """Checks if a value can be converted to a number.

    :param value: Value to be checked
    :type value: float | int | str
    :return: Is it a number, or not?
    :rtype: bool
    """

    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False


def is_date(value: Any) -> bool:
    """Checks if a value can be parsed as a date.

    This is a basic check. For more robust date parsing, consider
    using a dedicated library like 'dateutil.parser'

    :param value: Value to be checked
    :type value: Any
    :return: Is it a date, or not?
    :rtype: bool
    """
    if isinstance(value, datetime):
        return True
    try:
        pd.to_datetime(value)
        return True
    except (ValueError, TypeError):
        return False


def generate_random_string(length: int = 10, prefix: str = "ANON_") -> str:
    """Generates a random string.

    :param length: Length of the random part of the string, defaults to 10
    :type length: int, optional
    :param prefix: Prefix for the generated string, defaults to "ANON_"
    :type prefix: str, optional
    :return: The generated random string
    :rtype: str
    """
    random_part = "".join(random.choice(RANDOM_CHARS) for _ in range(length))
    return f"{prefix}{random_part}"


import re


def custom_mapping_replacement(
    word: str,
    mm: MappingTemplateManager,
) -> str:
    """
    Performs custom mapping replacement using pre-compiled regex patterns
    and a pre-processed lowercase template map from the MappingTemplateManager.

    :param word: The word to be replaced.
    :type word: str
    :param mm: An instance of MappingTemplateManager containing compiled patterns and map.
    :type mm: MappingTemplateManager
    :return: The replaced word, or the original word if no replacement is found.
    :rtype: str
    """
    word_str = str(word)

    for (
        compiled_pattern,
        replacement_value,
    ) in mm._compiled_custom_patterns:
        if compiled_pattern.search(word_str):
            return compiled_pattern.sub(replacement_value, word_str)

    if word_str in mm._compiled_map_template:
        template_value = mm._compiled_map_template[word_str]
        if str(template_value) != "":
            return str(template_value)
        else:
            return word_str

    return word_str


def generate_random_word_string(prefix: str = "ANON_") -> str:
    """Generates a random string using words from a predefined list.

    :param prefix: Prefix for the generated string, defaults to "ANON_"
    :type prefix: str, optional
    :return: The generated random word string
    :rtype: str
    """
    num_words = random.randint(1, 3)
    selected_words = random.sample(RANDOM_WORDS, num_words)
    return f"{prefix}{'_'.join(selected_words).upper()}"


def anonymise_email(email: str, keep_domain: bool = True) -> str:
    """
    Anonymises an email address while preserving its format.

    :param email: Original email address
    :type email: str
    :param keep_domain: Whether to keep the original domain or anonymise it, defaults to True
    :type keep_domain: bool, optional
    :return: Anonymised email address
    :rtype: str
    """
    if not isinstance(email, str):
        return email

    parts = email.split("@")
    if len(parts) != 2:
        return email

    username, domain = parts

    random_username = "".join(random.choice(RANDOM_CHARS) for _ in range(len(username)))

    if keep_domain:
        anonymised_domain = domain
    else:
        domain_parts = domain.split(".")
        anonymised_domain = ".".join(
            "".join(random.choice(RANDOM_CHARS) for _ in range(len(part)))
            for part in domain_parts
        )

    return f"{random_username}@{anonymised_domain}"


def anonymise_phone(phone: str) -> str:
    """
    Anonymises a phone number while preserving its format.

    :param phone: Original phone number
    :type phone: str
    :return: Anonymised phone number
    :rtype: str
    """
    if not isinstance(phone, str):
        return phone

    non_digits = "".join(c for c in phone if not c.isdigit())

    digits = "".join(
        random.choice("0123456789") for _ in range(sum(c.isdigit() for c in phone))
    )

    result = ""
    digit_index = 0
    for c in phone:
        if c.isdigit():
            result += digits[digit_index]
            digit_index += 1
        else:
            result += c

    return result


def is_identifiable_string(
    value: Any, exclude_patterns: str | list[str] | None = None
) -> bool:
    """
    Checks if a value is likely an identifiable string, with an option to exclude
    values matching specific regex patterns.

    :param value: The value to check
    :type value: Any
    :param exclude_patterns: A regex string or a list of regex strings. If the value
                             matches any of these patterns, it will not be considered
                             an identifiable string. Defaults to None.
    :type exclude_patterns: str | list[str] | None
    :return: True if the value is considered an identifiable string and does not
             match any exclusion patterns, False otherwise.
    :rtype: bool
    """
    if not isinstance(value, str):
        return False

    value_stripped = value.strip()
    if not value_stripped:
        return False

    if exclude_patterns:

        patterns_to_check = (
            [exclude_patterns]
            if isinstance(exclude_patterns, str)
            else exclude_patterns
        )
        for pattern in patterns_to_check:
            if re.search(pattern, value_stripped, re.IGNORECASE):
                return False

    if is_number(value_stripped) or is_date(value_stripped):
        return False

    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    phone_pattern = r"^[\d\s\-\(\)\+]*\d[\d\s\-\(\)\+]*$"

    if re.search(email_pattern, value_stripped):
        return True
    if re.search(phone_pattern, value_stripped):
        return True

    if re.search(r"[a-zA-Z]", value_stripped):
        return True

    return False
