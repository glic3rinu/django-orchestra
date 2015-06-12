import re


def extract_version_number(version):
    number = re.findall(r'[0-9]+\.?[0-9]?', version)
    if not number:
        raise ValueError("No version number matches for '%s'" % version)
    if len(number) > 1:
        raise ValueError("Multiple version number matches for '%s'" % version)
    return number[0]
