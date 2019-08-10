import os
import copy

import six
from six.moves.urllib.parse import urlparse

from ruamel.yaml.comments import CommentedMap, CommentedSeq

from .scriptcwl import load_cwl
from .reference import Reference


class PackedWorkflowException(Exception):
    """Error raised when trying to load a packed workflow."""
    pass


class Step(object):
    """Representation of a CWL step.

    The Step can be a CommandLineTool or a Workflow. Steps are read from file
    and validated using ``cwltool``.
    """

    def __init__(self, fname):
        fname = str(fname)
        if fname.startswith('http://') or fname.startswith('https://'):
            self.run = fname
            self.from_url = True
        else:
            self.run = os.path.abspath(fname)
            self.from_url = False

        bn = os.path.basename(fname)
        self.name = os.path.splitext(bn)[0]
        self.python_name = python_name(self.name)

        self.step_inputs = {}
        self.input_names = []
        self.input_types = {}
        self.optional_input_names = []
        self.optional_input_types = {}
        self.output_names = []
        self.output_types = {}
        self.is_workflow = False
        self.is_scattered = False
        self.scattered_inputs = []
        self.python_names = {}

        document_loader, processobj, metadata, uri = load_cwl(fname)
        s = processobj

        self.command_line_tool = s
        valid_classes = ('CommandLineTool', 'Workflow', 'ExpressionTool')
        if 'class' in s and s['class'] in valid_classes:
            self.is_workflow = s['class'] == 'Workflow'
            for inp in s['inputs']:
                # Due to preprocessing of cwltool the id has become an
                # absolute iri, for ease of use we keep only the fragment
                short_id = iri2fragment(inp['id'])
                if self._input_optional(inp):
                    self.optional_input_names.append(short_id)
                    self.optional_input_types[short_id] = inp['type']
                    self.python_names[python_name(short_id)] = short_id
                else:
                    self.input_names.append(short_id)
                    self.input_types[short_id] = inp['type']
                    self.python_names[python_name(short_id)] = short_id

            for o in s['outputs']:
                short_id = iri2fragment(o['id'])
                self.output_names.append(short_id)
                self.output_types[short_id] = o['type']
                self.python_names[python_name(short_id)] = short_id
        else:
            if isinstance(s, CommentedSeq):
                msg = 'Not loading "{}", because it is a packed workflow.'
                raise PackedWorkflowException(msg.format(self.run))
            else:
                msg = '"{}" is a unsupported'
                raise NotImplementedError(msg.format(self.name))

    def get_input_names(self):
        """Return the Step's input names (including optional input names).

        Returns:
            list of strings.
        """
        return self.input_names + self.optional_input_names

    def set_input(self, p_name, value):
        """Set a Step's input variable to a certain value.

        The value comes either from a workflow input or output of a previous
            step.

        Args:
            name (str): the name of the Step input
            value (str): the name of the output variable that provides the
                value for this input.

        Raises:
            ValueError: The name provided is not a valid input name for this
                Step.
        """
        name = self.python_names.get(p_name)
        if p_name is None or name not in self.get_input_names():
            raise ValueError('Invalid input "{}"'.format(p_name))
        self.step_inputs[name] = value

    def _set_name_in_workflow(self, name):
        self.name_in_workflow = name

    def output_reference(self, name):
        """Return a reference to the given output for use in an input
            of a next Step.

        For a Step named `echo` that has an output called `echoed`, the
        reference `echo/echoed` is returned.

        Args:
            name (str): the name of the Step output
        Raises:
            ValueError: The name provided is not a valid output name for this
                Step.
        """
        if name not in self.output_names:
            raise ValueError('Invalid output "{}"'.format(name))
        return Reference(step_name=self.name_in_workflow, output_name=name)

    @staticmethod
    def _input_optional(inp):
        """Returns True if a step input parameter is optional.

        Args:
            inp (dict): a dictionary representation of an input.

        Raises:
            ValueError: The inp provided is not valid.
        """
        if 'default' in inp.keys():
            return True

        typ = inp.get('type')
        if isinstance(typ, six.string_types):
            return typ.endswith('?')
        elif isinstance(typ, dict):
            # TODO: handle case where iput type is dict
            return False
        elif isinstance(typ, list):
            # The cwltool validation expands optional arguments to
            # [u'null', <type>]
            return bool(u'null' in typ)
        else:
            raise ValueError('Invalid input "{}"'.format(inp.get['id']))

    def _to_embedded_obj(self):
        embedded_clt = copy.deepcopy(self.command_line_tool)

        try:
            name_in_workflow = self.name_in_workflow
        except AttributeError:
            # Step has not yet been added to a workflow, so we use the step
            # name for the id fields of the embedded object.
            name_in_workflow = self.name

        # Remove shebang line
        # This is a bit magical, digging into ruamel.yaml, but there
        # does not seem to be a better way.
        try:
            global_comments = embedded_clt.ca.comment[1]
        except TypeError:
            global_comments = None
        if global_comments:
            if global_comments[0].value.startswith('#!'):
                del(global_comments[0])

        # Give inputs and outputs a JSON-LD local identifier, instead of
        # the default absolute path that doesn't exist on other machines.
        def to_local_id(iri, name_in_workflow):
            parsed_iri = urlparse(iri)
            input_id = name_in_workflow
            if parsed_iri.fragment:
                input_id += '#' + parsed_iri.fragment
            if not input_id.startswith('_:'):
                input_id = '_:' + input_id
            return input_id

        for inp in embedded_clt['inputs']:
            inp['id'] = to_local_id(inp['id'], name_in_workflow)

        for outp in embedded_clt['outputs']:
            outp['id'] = to_local_id(outp['id'], name_in_workflow)

        embedded_clt['id'] = to_local_id(embedded_clt['id'], name_in_workflow)

        # If the step is a (sub)workflow, the source fields of the steps in the
        # workflow must be removed.
        if embedded_clt['class'] == 'Workflow':
            for step in embedded_clt['steps']:
                for inp in step['in']:
                    del inp['source']

        return embedded_clt

    def to_obj(self, wd=False, pack=False, relpath=None):
        """Return the step as an dict that can be written to a yaml file.

        Returns:
            dict: yaml representation of the step.
        """
        obj = CommentedMap()
        if pack:
            obj['run'] = self.orig
        elif relpath is not None:
            if self.from_url:
                obj['run'] = self.run
            else:
                obj['run'] = os.path.relpath(self.run, relpath)
        elif wd:
            if self.from_url:
                obj['run'] = self.run
            else:
                obj['run'] = os.path.basename(self.run)
        else:
            obj['run'] = self.run
        obj['in'] = self.step_inputs
        obj['out'] = self.output_names
        if self.is_scattered:
            obj['scatter'] = self.scattered_inputs
            # scatter_method is optional when scattering over a single variable
            if self.scatter_method is not None:
                obj['scatterMethod'] = self.scatter_method

        return obj

    def __str__(self):
        if self.optional_input_names:
            template = u'{} = wf.{}({}[, {}])'
        else:
            template = u'{} = wf.{}({})'
        out_names = [python_name(n) for n in self.output_names]
        in_names = [python_name(n) for n in self.input_names]
        opt_in_names = [python_name(n) for n in self.optional_input_names]
        return template.format(u', '.join(out_names), self.python_name,
                               u', '.join(in_names), u', '.join(
                                   opt_in_names))

    def __repr__(self):
        return str(self)

    def list_inputs(self):
        """Return a string listing all the Step's input names and their types.

        The types are returned in a copy/pastable format, so if the type is
        `string`, `'string'` (with single quotes) is returned.

        Returns:
            str containing all input names and types.
        """
        doc = []
        for inp, typ in self.input_types.items():
            if isinstance(typ, six.string_types):
                typ = "'{}'".format(typ)
            doc.append('{}: {}'.format(inp, typ))
        return '\n'.join(doc)


def iri2fragment(iri):
    """Return the fragment of an IRI.

    Args:
        iri (str): the iri.

    Returns:
        str: the fragment of the iri.
    """
    o = urlparse(iri)
    return o.fragment


def python_name(name):
    """Transform cwl step name into a python method name.

    Args:
        name (str): CWL step name to convert.

    Returns:
        str: converted name.
    """
    name = name.replace('-', '_')

    return name
