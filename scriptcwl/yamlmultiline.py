"""Functionality for properly formatting multi line strings in yaml.

Source: http://stackoverflow.com/a/33300001
"""


def is_multiline(s):
    return len(s.splitlines()) > 1


def str_presenter(dmpr, data):
    if is_multiline(data):
        return dmpr.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dmpr.represent_scalar('tag:yaml.org,2002:str', data)
