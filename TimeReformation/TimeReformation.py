import re


def iso8601_to_normal(iso_string):
    pattern = re.compile(
        r'P(?:[0-9]+Y)?(?:[0-9]+M)?(?:[0-9]+W)?(?:[0-9]+D)?(?:T(?:([0-9]+)H)?(?:([0-9]+)M)?(?:([0-9]+)S)?)?')

    match = pattern.match(iso_string)
    if match:
        hours = int(match.group(1)) if match.group(1) else 0
        minutes = int(match.group(2)) if match.group(2) else 0
        seconds = int(match.group(3)) if match.group(3) else 0

        total_minutes = hours * 60 + minutes + seconds / 60
        return total_minutes
    else:
        return iso_string
