import os
import glob
import shutil
import logging

from six.moves.urllib.parse import urlparse

from schema_salad.validate import ValidationException

from .scriptcwl import is_url
from .step import Step, PackedWorkflowException

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
fh = logging.StreamHandler()
fh_formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
fh.setFormatter(fh_formatter)
logger.addHandler(fh)


class StepsLibrary(object):
    """Oject to store steps that can be used to build workflows
    """
    def __init__(self, working_dir=None):
        self.steps = {}
        self.step_ids = []
        self.working_dir = working_dir

    def load(self, steps_dir=None, step_file=None, step_list=None):
        steps_to_load = load_steps(working_dir=self.working_dir,
                                   steps_dir=steps_dir,
                                   step_file=step_file,
                                   step_list=step_list)

        for n, step in steps_to_load.items():
            if n in self.steps.keys():
                print('WARNING: step "{}" already in steps library'.format(n))
            else:
                if step.is_workflow:
                    for substep in step.command_line_tool['steps']:
                        self.step_ids.append(name_in_workflow(substep['id']))
                self.steps[n] = step

    def get_step(self, name):
        return self.steps.get(name)

    def list_steps(self):
        steps = []
        workflows = []
        template = u'  {:.<25} {}'
        for name, step in self.steps.items():
            if step.is_workflow:
                workflows.append(template.format(name, step))
            else:
                steps.append(template.format(name, step))

        steps.sort()
        workflows.sort()
        result = [u'Steps\n', u'\n'.join(steps), u'\n\nWorkflows\n',
                  u'\n'.join(workflows)]
        return u''.join(result)


def name_in_workflow(iri):
    """Extract the name of a step in a subworkflow.
    """
    parsed_iri = urlparse(iri)
    if parsed_iri.fragment:
        return parsed_iri.fragment
    return None


def load_steps(working_dir=None, steps_dir=None, step_file=None,
               step_list=None):
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
        if working_dir is not None:
            # Copy file to working_dir
            if not working_dir == os.path.dirname(f) and not is_url(f):
                copied_file = os.path.join(working_dir, os.path.basename(f))
                shutil.copy2(f, copied_file)

        # Create steps from orgininal files
        try:
            s = Step(f)
            steps[s.name] = s
        except (NotImplementedError, ValidationException,
                PackedWorkflowException) as e:
            logger.warning(e)

    return steps
