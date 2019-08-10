import os
import glob
import shutil
import logging
import sys
import warnings

from six.moves.urllib.parse import urlparse

from schema_salad.validate import ValidationException

from ruamel import yaml

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
        self.python_names2step_names = {}

    def load(self, steps_dir=None, step_file=None, step_list=None):
        steps_to_load = load_steps(working_dir=self.working_dir,
                                   steps_dir=steps_dir,
                                   step_file=step_file,
                                   step_list=step_list)

        for n, step in steps_to_load.items():
            if n in self.steps.keys():
                msg = 'Step "{}" already in steps library.'.format(n)
                warnings.warn(UserWarning(msg))
            elif step.python_name in self.python_names2step_names.keys():
                pn = self.python_names2step_names.get(step.python_name)
                msg = 'step "{}.cwl" has the same python name as "{}.cwl". ' \
                      'Please rename file "{}.cwl", so it can be ' \
                      'loaded.'.format(n, pn, n)
                warnings.warn(UserWarning(msg))
            else:
                self.steps[n] = step
                self.python_names2step_names[step.python_name] = n

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

    if working_dir is not None:
        step_files = sort_loading_order(step_files)

    steps = {}
    for f in step_files:
        if working_dir is not None:
            # Copy file to working_dir
            if not working_dir == os.path.dirname(f) and not is_url(f):
                copied_file = os.path.join(working_dir, os.path.basename(f))
                shutil.copy2(f, copied_file)
                f = copied_file

        # Create steps
        try:
            s = Step(f)
            steps[s.name] = s
        except (NotImplementedError, ValidationException,
                PackedWorkflowException) as e:
            logger.warning(e)

    return steps


def load_yaml(filename):
    """Return object in yaml file."""
    with open(filename) as myfile:
        content = myfile.read()
        if "win" in sys.platform:
            content = content.replace("\\", "/")

        try:
            obj = yaml.safe_load(content)

            # packed workflow, will be ignored later
            if obj.get('$graph'):
                obj = {}
        # packed workflow, will be ignored later
        # (it seems in some cases a packed workflow gives an ParserError, while
        # in other cases it is loaded correctly)
        except yaml.parser.ParserError:
            obj = {}
        return obj


def sort_loading_order(step_files):
    """Sort step files into correct loading order.

    The correct loading order is first tools, then workflows without
    subworkflows, and then workflows with subworkflows. This order is
    required to avoid error messages when a working directory is used.
    """
    tools = []
    workflows = []
    workflows_with_subworkflows = []

    for f in step_files:
        # assume that urls are tools
        if f.startswith('http://') or f.startswith('https://'):
            tools.append(f)
        else:
            obj = load_yaml(f)
            if obj.get('class', '') == 'Workflow':
                if 'requirements' in obj.keys():
                    subw = {'class': 'SubworkflowFeatureRequirement'}
                    if subw in obj['requirements']:
                        workflows_with_subworkflows.append(f)
                    else:
                        workflows.append(f)
                else:
                    workflows.append(f)
            else:
                tools.append(f)
    return tools + workflows + workflows_with_subworkflows
