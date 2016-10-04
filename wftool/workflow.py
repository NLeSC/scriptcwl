from functools import partial


class WorkflowGenerator(object):

    def __init__(self):
        self.wf_steps = {}
        self.wf_inputs = {}
        self.wf_outputs = {}
        self.step_output_types = {}
        self.steps_library = {}

    def __getattr__(self, name, **kwargs):
        try:
            return super(self.__class__, self).__getattr__(name)
        except AttributeError:
            name = cwl_name(name)
            step = self._get_step(name)
            for n in step.output_names:
                oname = step.output_to_input(n)
                self.step_output_types[oname] = step.step_outputs[n]
            return partial(self._make_step, step, **kwargs)

    def load(self, steps):
        self.steps_library = steps

    def list_steps(self):
        for name, step in self.steps_library.iteritems():
            print 'Step "{}": {}'.format(name, step)

    def inputs(self, name):
        """List input names and types of a step in the steps library.
        """
        s = self._get_step(name)
        print s.list_inputs()

    def _add_step(self, step):
        self.wf_steps[step.name] = step.to_obj()

    def add_input(self, name, typ):
        """Add workflow input with name name and type typ.

        Returns: name
        """
        self.wf_inputs[name] = typ
        return name

    def add_output(self, **kwargs):
        """Add workflow outputs.

        kwargs is a dict of name=source name. name is the name of the workflow
        output (e.g., `txt_files`) and source name is the name of the step that
        produced this output plus the output name (e.g.,
        `saf-to-txt/out_files`). The output type is added automatically, based
        on the steps in the steps library.
        """
        for name, source_name in kwargs.iteritems():
            obj = {}
            obj['outputSource'] = source_name
            obj['type'] = self.step_output_types[source_name]
            self.wf_outputs[name] = obj

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
        obj['inputs'] = self.wf_inputs
        obj['outputs'] = self.wf_outputs
        obj['steps'] = self.wf_steps
        return obj

    def _make_step(self, step, **kwargs):
        for k in step.input_names:
            if k not in kwargs.keys():
                raise ValueError(
                    'Expecting "{}" as a keyword argument.'.format(k))
            step.set_input(k, kwargs[k])
        self._add_step(step)
        outputs = [step.output_to_input(n) for n in step.output_names]
        if len(outputs) == 1:
            return outputs[0]
        return outputs


def cwl_name(name):
    """Transform python name to cwl name.
    """
    name = name.replace('_', '-')

    return name
