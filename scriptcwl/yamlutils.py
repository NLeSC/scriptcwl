"""Functionality for saving yaml files.
"""
import codecs

from ruamel import yaml

from .reference import Reference, reference_presenter


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


def save_yaml(fname, wf, inline, pack, relpath, wd, encoding='utf-8'):
    with codecs.open(fname, 'wb', encoding=encoding) as yaml_file:
        yaml_file.write('#!/usr/bin/env cwl-runner\n')
        yaml_file.write(yaml.dump(wf.to_obj(inline=inline,
                                            pack=pack,
                                            relpath=relpath,
                                            wd=wd),
                                  Dumper=yaml.RoundTripDumper))


yaml.add_representer(str, str_presenter, Dumper=yaml.RoundTripDumper)
yaml.add_representer(Reference, reference_presenter,
                     Dumper=yaml.RoundTripDumper)
