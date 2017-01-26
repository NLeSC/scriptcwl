"""Functionality for properly formatting multi line strings in yaml.
"""


def is_multiline(s):
    """Return True if a str consists of multiple lines.

    Args:
        s (str): the string to check.

    Returns:
        bool
    """
    return len(s.splitlines()) > 1


def str_presenter(dmpr, data):
    """Return correct str_presenter to write multiple lines to a yaml field.

    Source: http://stackoverflow.com/a/33300001
    """
    if is_multiline(data):
        return dmpr.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dmpr.represent_scalar('tag:yaml.org,2002:str', data)
