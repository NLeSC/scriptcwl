import yaml
import os
import codecs

from functools import partial

from .scriptcwl import load_steps
from .step import Step, python_name
from .yamlmultiline import str_presenter, is_multiline


class WorkflowGenerator(object):

    def __init__(self, steps_dir=None):
        self.wf_steps = {}
        self.wf_inputs = {}
        self.wf_outputs = {}
        self.step_output_types = {}
        self.steps_library = {}

        self.load(steps_dir)

    def __getattr__(self, name, **kwargs):
        name = cwl_name(name)
        step = self._get_step(name)
        for n in step.output_names:
            oname = step.output_to_input(n)
            self.step_output_types[oname] = step.step_outputs[n]
        return partial(self._make_step, step, **kwargs)

    def load(self, steps_dir=None, step_file=None):
        steps = load_steps(steps_dir=steps_dir, step_file=step_file)
        for n, step in steps.iteritems():
            if n in self.steps_library.keys():
                print 'WARNING: step "{}" already in steps library'.format(n)
            else:
                self.steps_library[n] = step

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

    def add_inputs(self, **kwargs):
        """Add workflow inputs.
        kwargs is a dict with `name=type`, where name is the name (id) of the
        workflow input (e.g., `dir_in`) and type is the type of the input
        (e.g., `'Directory'`). The type of input parameters can be learned from
        `step.inputs(step_name=input_name)`.

        Returns: list of names
        """
        names = []
        for name, typ in kwargs.iteritems():
            self.wf_inputs[name] = typ
            names.append(name)

        if len(names) == 1:
            return names[0]
        return names

    def add_outputs(self, **kwargs):
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

    def set_documentation(self, doc):
        self.documentation = doc

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
        try:
            obj['doc'] = self.documentation
        except (AttributeError, ValueError):
            pass
        obj['inputs'] = self.wf_inputs
        obj['outputs'] = self.wf_outputs
        obj['steps'] = self.wf_steps
        return obj

    def to_script(self, wf_name='wf'):

        # Workflow documentation
        if self.documentation:
            if is_multiline(self.documentation):
                print 'doc = """'
                print self.documentation
                print '"""'
                print '{}.set_documentation(doc)'.format(wf_name)
            else:
                print '{}.set_documentation(\'{}\')'.format(wf_name, self.documentation)

        # Workflow inputs
        params = []
        returns = []
        for name, typ in self.wf_inputs.iteritems():
            params.append('{}=\'{}\''.format(name, typ))
            returns.append(name)
        print '{} = {}.add_inputs({})'.format(', '.join(returns), wf_name,
                                              ', '.join(params))

        # Workflow steps
        returns = []
        for name, step in self.wf_steps.iteritems():
            s = Step(step['run'])
            returns = ['{}_{}'.format(python_name(s.name), o) for o in step['out']]
            params = ['{}={}'.format(name, python_name(param)) for name, param in step['in'].iteritems()]
            print '{} = {}.{}({})'.format(', '.join(returns), wf_name, s.python_name, ', '.join(params))

        # Workflow outputs
        params = []
        for name, details in self.wf_outputs.iteritems():
            params.append('{}={}'.format(name, python_name(details['outputSource'])))
        print '{}.add_outputs({})'.format(wf_name, ', '.join(params))

    def _make_step(self, step, **kwargs):
        for k in step.get_input_names():
            if k not in kwargs.keys() and k not in step.optional_input_names:
                raise ValueError(
                    'Expecting "{}" as a keyword argument.'.format(k))
            if kwargs.get(k):
                step.set_input(k, kwargs[k])
        self._add_step(step)
        outputs = [step.output_to_input(n) for n in step.output_names]
        if len(outputs) == 1:
            return outputs[0]
        return outputs

    def save(self, fname, encoding='utf-8'):
        dirname = os.path.dirname(os.path.abspath(fname))

        if not os.path.exists(dirname):
            os.makedirs(dirname)

        yaml.add_representer(str, str_presenter)
        with codecs.open(fname, 'wb', encoding=encoding) as yaml_file:
            yaml.dump(self.to_obj(), yaml_file, default_flow_style=False)


def cwl_name(name):
    """Transform python name to cwl name.
    """
    name = name.replace('_', '-')

    return name
