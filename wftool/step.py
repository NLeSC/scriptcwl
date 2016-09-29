import yaml
import os


class Step:
    def __init__(self, fname, abspath=True, start=os.curdir):
        if abspath:
            self.run = os.path.abspath(fname)
        else:
            self.run = os.path.relpath(fname, start)

        bn = os.path.basename(fname)
        self.name = os.path.splitext(bn)[0]

        self.inputs = {}

        with open(fname) as f:
            s = yaml.load(f)

            self.input_names = [i['id'] for i in s['inputs']]
            self.output_names = [i['id'] for i in s['outputs']]

            self.outputs = {}
            for o in s['outputs']:
                self.outputs[o['id']] = o['type']

    def set_input(self, name, value):
        if name not in self.input_names:
            raise ValueError('Invalid input "{}"'.format(name))
        self.inputs[name] = value

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
        obj['in'] = self.inputs
        obj['out'] = [self.output_names[0]]

        return obj
