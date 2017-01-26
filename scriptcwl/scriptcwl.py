import glob
import logging
from schema_salad.validate import ValidationException

from .step import Step


def load_steps(steps_dir=None, step_file=None):
    """Return a dictionary containing Steps read from file.

    Args:
        steps_dir (str, optional): path to directory containing CWL files.
        step_file (str, optional): path to a single CWL file.

    Return:
        dict containing (name, Step) entries.

    """
    if steps_dir is not None:
        step_files = glob.glob('{}/*.cwl'.format(steps_dir))
    elif step_file is not None:
        step_files = [step_file]
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
