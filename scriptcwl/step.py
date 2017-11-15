import os
import sys
import copy
from contextlib import contextmanager

import six
from six.moves.urllib.parse import urlparse

from ruamel.yaml.comments import CommentedMap

from .reference import Reference


# Helper function to make the import of cwltool.load_tool quiet
@contextmanager
def quiet():
    # save stdout/stderr
    # Jupyter doesn't support setting it back to
    # sys.__stdout__ and sys.__stderr__
    _sys_stdout = sys.stdout
    _sys_stderr = sys.stderr
    # Divert stdout and stderr to devnull
    sys.stdout = sys.stderr = open(os.devnull, "w")
    try:
        yield
    finally:
        # Revert back to standard stdout/stderr
        sys.stdout = _sys_stdout
        sys.stderr = _sys_stderr


# import cwltool.load_tool functions
with quiet():
    # all is quiet in this scope
    from cwltool.load_tool import fetch_document, validate_document


class Step(object):
    """Representation of a CWL step.

    The Step can be a CommandLineTool or a Workflow. Steps are read from file
    and validated using ``cwltool``.
    """

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
        self.optional_input_names = []
        self.optional_input_types = {}
        self.output_names = []
        self.output_types = {}
        self.is_workflow = False
        self.is_scattered = False
        self.scattered_inputs = []

        # Fetching, preprocessing and validating cwl
        (document_loader, workflowobj, uri) = fetch_document(fname)
        (document_loader, _, processobj, _, uri) = \
            validate_document(document_loader, workflowobj, uri)
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
                else:
                    self.input_names.append(short_id)
                    self.input_types[short_id] = inp['type']

            for o in s['outputs']:
                short_id = iri2fragment(o['id'])
                self.output_names.append(short_id)
                self.output_types[short_id] = o['type']
        else:
            msg = '"{}" is a unsupported'
            raise NotImplementedError(msg.format(self.name))

    def get_input_names(self):
        """Return the Step's input names (including optional input names).

        Returns:
            list of strings.
        """
        return self.input_names + self.optional_input_names

    def set_input(self, name, value):
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
        if name not in self.get_input_names():
            raise ValueError('Invalid input "{}"'.format(name))
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

        # Remove shebang line
        # This is a bit magical, digging into ruamel.yaml, but there
        # does not seem to be a better way.
        global_comments = embedded_clt.ca.comment[1]
        if global_comments:
            if global_comments[0].value.startswith('#!'):
                del(global_comments[0])

        # Give inputs and outputs a JSON-LD local identifier, instead of
        # the default absolute path that doesn't exist on other machines.
        def to_local_id(iri):
            parsed_iri = urlparse(iri)
            input_id = parsed_iri.path.split('/')[-1]
            if parsed_iri.fragment:
                input_id += '#' + parsed_iri.fragment
            if not input_id.startswith('_:'):
                input_id = '_:' + input_id
            return input_id

        for inp in embedded_clt['inputs']:
            inp['id'] = to_local_id(inp['id'])

        for outp in embedded_clt['outputs']:
            outp['id'] = to_local_id(outp['id'])

        embedded_clt['id'] = to_local_id(embedded_clt['id'])

        return embedded_clt

    def to_obj(self, inline=True, relpath=None):
        """Return the step as an dict that can be written to a yaml file.

        Returns:
            dict: yaml representation of the step.
        """
        obj = CommentedMap()
        if inline:
            obj['run'] = self._to_embedded_obj()
        elif relpath is not None:
            obj['run'] = os.path.relpath(self.run, relpath)
        else:
            obj['run'] = self.run
        obj['in'] = self.step_inputs
        obj['out'] = self.output_names
        if self.is_scattered:
            obj['scatter'] = self.scattered_inputs
            obj['scatterMethod'] = self.scatter_method

        return obj

    def __str__(self):
        if self.optional_input_names:
            template = u'{} = wf.{}({}[, {}])'
        else:
            template = u'{} = wf.{}({})'
        return template.format(u', '.join(self.output_names), self.python_name,
                               u', '.join(self.input_names), u', '.join(
                                   self.optional_input_names))

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
