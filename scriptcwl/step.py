import yaml
import os
import six


class Step:
    def __init__(self, fname, abspath=True, start=os.curdir):
        if abspath:
            self.run = os.path.abspath(fname)
        else:
            self.run = os.path.relpath(fname, start)

        bn = os.path.basename(fname)
        self.name = os.path.splitext(bn)[0]
        self.python_name = python_name(self.name)

        self.step_inputs = {}
        self.input_names = []
        self.input_types = {}
        self.output_names = []
        self.step_outputs = {}

        with open(fname) as f:
            s = yaml.load(f)

            if s['class'] == 'CommandLineTool':
                for inp in s['inputs']:
                    self.input_names.append(inp['id'])
                    self.input_types[inp['id']] = inp['type']

                    self.output_names = [i['id'] for i in s['outputs']]

                    for o in s['outputs']:
                        self.step_outputs[o['id']] = o['type']
            else:
                # TODO: deal with subworkflows (issue #4)
                msg = 'Warning: "{}" is a Workflow, not a CommandLineTool'
                print msg.format(self.name)

    def set_input(self, name, value):
        if name not in self.input_names:
            raise ValueError('Invalid input "{}"'.format(name))
        self.step_inputs[name] = value

    def get_input(self, name):
        if name not in self.input_names:
            raise ValueError('Invalid input "{}"'.format(name))
        return ''.join(self.name, '/', )

    def output_to_input(self, name):
        if name not in self.output_names:
            raise ValueError('Invalid output "{}"'.format(name))
        return ''.join([self.name, '/', name])

    def to_obj(self):
        obj = {}
        obj['run'] = self.run
        obj['in'] = self.step_inputs
        obj['out'] = [self.output_names[0]]

        return obj

    def __str__(self):
        template = '{} = {}({})'
        return template.format(', '.join(self.output_names), self.python_name,
                               ', '.join(self.input_names))

    def list_inputs(self):
        doc = []
        for inp, typ in self.input_types.iteritems():
            if isinstance(typ, six.string_types):
                typ = "'{}'".format(typ)
            doc.append('{}: {}'.format(inp, typ))
        return '\n'.join(doc)


def python_name(name):
    """Transform cwl step name into a python method name.
    """
    name = name.replace('-', '_')

    return name
