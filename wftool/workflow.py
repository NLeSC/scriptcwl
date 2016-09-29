from functools import partial


class WorkflowGenerator(object):

    def __init__(self):
        self.steps = {}
        self.inputs = {}
        self.outputs = {}
        self.steps_library = {}

    def __getattr__(self, name, **kwargs):
        try:
            return super(self.__class__, self).__getattr__(name)
        except AttributeError:
            print name
            name = cwl_name(name)
            print name
            return partial(self._make_step, name, **kwargs)

    def load(self, steps):
        self.steps_library = steps

    def list_steps(self):
        for name, step in self.steps_library.iteritems():
            print 'Step "{}": {}'.format(name, step)

    def _add_step(self, step):
        self.steps[step.name] = step.to_obj()

    def _add_input(self, name, typ):
        self.inputs[name] = typ

    def _add_output(self, output_name, source_name, step):
        obj = {}
        obj['type'] = step.outputs[source_name]
        obj['outputSource'] = step.output_to_input(source_name)

        self.outputs[output_name] = obj

    def _get_step(self, name):
        s = self.steps_library.get(name)
        if s is None:
            msg = '"{}" not found in steps library. Please check your ' \
                  'spelling or load additional steps'
            raise ValueError(msg.format(name))
        return s

    def to_obj(self):
        obj = {}
        obj['cwlVersion'] = 'v1.0'
        obj['class'] = 'Workflow'
        obj['inputs'] = self.inputs
        obj['outputs'] = self.outputs
        obj['steps'] = self.steps
        return obj

    def _make_step(self, name, **kwargs):
        s = self._get_step(name)

        for k in s.input_names:
            if k not in kwargs.keys():
                raise ValueError(
                    'Expecting "{}" as a keyword argument.'.format(k))
            s.set_input(k, kwargs[k])
        self._add_step(s)
        outputs = [s.output_to_input(n) for n in s.output_names]
        if len(outputs) == 1:
            return outputs[0]
        return outputs


def cwl_name(name):
    """Transform python name to cwl name.
    """
    name = name.replace('_', '-')

    return name
