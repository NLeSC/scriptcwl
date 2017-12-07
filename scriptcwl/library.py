import os
import shutil

from six.moves.urllib.parse import urlparse

from .scriptcwl import load_steps


class StepsLibrary(object):
    """Oject to store steps that can be used to build workflows
    """
    def __init__(self, working_dir=None):
        self.steps = {}
        self.step_ids = []
        self.working_dir = working_dir
        if self.working_dir:
            self.working_dir = os.path.abspath(working_dir)
            # TODO: empty dir if it contains files?
            if not os.path.exists(self.working_dir):
                os.makedirs(self.working_dir)
        self.implicit_working_dir = False

    def load(self, steps_dir=None, step_file=None, step_list=None):
        steps_to_load = load_steps(steps_dir=steps_dir, step_file=step_file,
                                   step_list=step_list)
        for n, step in steps_to_load.items():
            dir_name = os.path.dirname(step.run)
            if not self.working_dir:
                # set working dir implicitly
                self.working_dir = dir_name
                self.implicit_working_dir = True

            if self.working_dir != dir_name:
                if self.implicit_working_dir:
                    msg = 'Trying to load a step from "{}". This directory ' \
                          'is not the same as the implicit working directory' \
                          ' "{}".\n\nPlease set a working directory when ' \
                          'creating the WorkflowGenerator object (Workflow' \
                          'Generator(working_dir=/path/to/working/directory/' \
                          ')).'.format(dir_name, self.working_dir)
                    raise ValueError(msg)
                else:
                    new_run = self._copy_to_working_dir(step)
                    step.run = new_run

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

    def _copy_to_working_dir(self, step):
        """Copy cwl files to a directory where the cwl-runner can find them.

        Args:
        """
        fo = os.path.join(self.working_dir, os.path.basename(step.run))
        shutil.copy2(step.run, fo)
        return fo


def name_in_workflow(iri):
    """Extract the name of a step in a subworkflow.
    """
    parsed_iri = urlparse(iri)
    if parsed_iri.fragment:
        return parsed_iri.fragment
    return None
