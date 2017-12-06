from six.moves.urllib.parse import urlparse


class StepsLibrary(object):
    """Oject to store steps that can be used to build workflows
    """
    def __init__(self):
        self.steps = {}
        self.step_ids = []

    def load(self, steps_to_load):
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
