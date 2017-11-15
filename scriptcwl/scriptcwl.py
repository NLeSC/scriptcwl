import os
import glob
import logging

from schema_salad.validate import ValidationException

from .step import Step


def load_steps(steps_dir=None, step_file=None, step_list=None):
    """Return a dictionary containing Steps read from file.

    Args:
        steps_dir (str, optional): path to directory containing CWL files.
        step_file (str, optional): path or http(s) url to a single CWL file.
        step_list (list, optional): a list of directories, urls or local file
            paths to CWL files or directories containing CWL files.

    Return:
        dict containing (name, Step) entries.

    """
    if steps_dir is not None:
        step_files = glob.glob(os.path.join(steps_dir, '*.cwl'))
    elif step_file is not None:
        step_files = [step_file]
    elif step_list is not None:
        step_files = []
        for path in step_list:
            if os.path.isdir(path):
                step_files += glob.glob(os.path.join(path, '*.cwl'))
            else:
                step_files.append(path)
    else:
        step_files = []

    steps = {}
    for f in step_files:
        try:
            s = Step(f)
            steps[s.name] = s
        except (NotImplementedError, ValidationException) as e:
            logging.warning(e)

    return steps
