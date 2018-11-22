from __future__ import print_function

import codecs
import copy
import os
import shutil
from functools import partial

import tempfile
import six
from ruamel.yaml.comments import CommentedMap

from .scriptcwl import load_cwl, quiet
from .step import python_name
from .yamlutils import save_yaml, yaml2string
from .library import StepsLibrary
from .reference import Reference

import warnings

# import cwltool.load_tool functions
with quiet():
    # all is quiet in this scope
    from cwltool.main import print_pack

warnings.simplefilter('always', DeprecationWarning)


class WorkflowGenerator(object):
    """Class for creating a CWL workflow.

    The WorkflowGenerator class allows users to tie together inputs and outputs
    of the steps that need to be executed to perform a data processing task.
    The steps (i.e., command line tools and subworkflows) must be added to the
    steps library of the WorkflowGenerator object before they can be added to
    the workflow. To add steps to the steps library, the `load` method can be
    called with either a path to a directory containing CWL files:
    ::

        from scriptcwl import WorkflowGenerator

        with WorkflowGenerator() as wf:
            wf.load(steps_dir='/path/to/dir/with/cwl/steps/')

    Or a single CWL file:
    ::

        with WorkflowGenerator() as wf:
            wf.load(step_file='/path/to/cwl/step/file')

    ``wf.load()`` can be called multiple times. Step files are added to the
    steps library one after the other. For every step that is added to the
    steps library, a method with the same name is added to the
    WorkflowGenerator object. To add a step to the workflow, this method must
    be called (examples below).

    Next, the user should add one or more workflow inputs:
    ::
      txt_dir = wf.add_input(txt_dir='Directory')

    The ``add_input()`` method expects a ``name=type`` pair as input parameter.
    The pair connects an input name (``txt_dir`` in the example) to a CWL type
    (``'Directory'``). Optionally, a default value can be specified using
    ``default=value``.

    The ``add_input()`` method returns a string containing the name
    that can be used to connect this input parameter to step input parameter
    names.

    Next, workflow steps can be added. To add a workflow step, its method must
    be called on the WorkflowGenerator object. This method expects a list of
    (key, value) pairs as input parameters. (To find out what inputs a step
    needs call ``wf.inputs(<step name>)``. This method prints all the inputs
    and their types.) The method returns a list of strings containing output
    names that can be used as input for later steps, or that can be connected
    to workflow outputs.

    For example, to add a step called ``frog-dir`` to the workflow, the
    following method must be called:
    ::

        frogout = wf.frog_dir(dir_in=txt_dir)

    In a next step, ``frogout`` can be used as input:
    ::
        saf = wf.frog_to_saf(in_files=frogout)
        txt = wf.saf_to_txt(in_files=saf)

    Etcetera.

    When all steps of the workflow have been added, the user can specify
    workflow outputs:
    ::

        wf.add_outputs(txt=txt)

    Finally, the workflow can be saved to file:
    ::

        wf.save('workflow.cwl')

    To list steps and signatures available in the steps library, call:
    ::

        wf.list_steps()
    """

    def __init__(self, steps_dir=None, working_dir=None):
        self.working_dir = working_dir
        if self.working_dir:
            self.working_dir = os.path.abspath(self.working_dir)
            if not os.path.exists(self.working_dir):
                os.makedirs(self.working_dir)
        self.wf_steps = CommentedMap()
        self.wf_inputs = CommentedMap()
        self.wf_outputs = CommentedMap()
        self.step_output_types = {}
        self.steps_library = StepsLibrary(working_dir=working_dir)
        self.has_workflow_step = False
        self.has_scatter_requirement = False
        self.has_multiple_inputs = False

        self._wf_closed = False

        self.load(steps_dir)

    def __enter__(self):
        self._wf_closed = False

        return self

    def __exit__(self, *args):
        self.wf_steps = None
        self.wf_inputs = None
        self.wf_outputs = None
        self.step_output_types = None
        self.steps_library = None
        self.has_workflow_step = None
        self.has_scatter_requirement = None
        self.working_dir = None

        self._wf_closed = True

    def __getattr__(self, name, **kwargs):
        name = self.steps_library.python_names2step_names.get(name, None)
        step = self._get_step(name)
        return partial(self._make_step, step, **kwargs)

    def __str__(self):
        # use absolute paths for printing
        return yaml2string(self,
                           pack=False,
                           relpath=None,
                           wd=False)

    def _closed(self):
        if self._wf_closed:
            raise ValueError('Operation on closed WorkflowGenerator.')

    def load(self, steps_dir=None, step_file=None, step_list=None):
        """Load CWL steps into the WorkflowGenerator's steps library.

        Adds steps (command line tools and workflows) to the
        ``WorkflowGenerator``'s steps library. These steps can be used to
        create workflows.

        Args:
            steps_dir (str): path to directory containing CWL files. All CWL in
                the directory are loaded.
            step_file (str): path to a file containing a CWL step that will be
                added to the steps library.
        """
        self._closed()

        self.steps_library.load(steps_dir=steps_dir, step_file=step_file,
                                step_list=step_list)

    def list_steps(self):
        """Return string with the signature of all steps in the steps library.
        """
        self._closed()

        return self.steps_library.list_steps()

    def _has_requirements(self):
        """Returns True if the workflow needs a requirements section.

        Returns:
            bool: True if the workflow needs a requirements section, False
                otherwise.
        """
        self._closed()

        return any([self.has_workflow_step, self.has_scatter_requirement,
                   self.has_multiple_inputs])

    def inputs(self, name):
        """List input names and types of a step in the steps library.

        Args:
            name (str): name of a step in the steps library.
        """
        self._closed()

        step = self._get_step(name, make_copy=False)
        return step.list_inputs()

    def _add_step(self, step):
        """Add a step to the workflow.

        Args:
            step (Step): a step from the steps library.
        """
        self._closed()

        self.has_workflow_step = self.has_workflow_step or step.is_workflow
        self.wf_steps[step.name_in_workflow] = step

    def add_input(self, **kwargs):
        """Add workflow input.

        Args:
            kwargs (dict): A dict with a `name: type` item
                and optionally a `default: value` item, where name is the
                name (id) of the workflow input (e.g., `dir_in`) and type is
                the type of the input (e.g., `'Directory'`).
                The type of input parameter can be learned from
                `step.inputs(step_name=input_name)`.

        Returns:
            inputname

        Raises:
            ValueError: No or multiple parameter(s) have been specified.
        """
        self._closed()

        def _get_item(args):
            """Get a single item from args."""
            if not args:
                raise ValueError("No parameter specified.")
            item = args.popitem()
            if args:
                raise ValueError("Too many parameters, not clear what to do "
                                 "with {}".format(kwargs))
            return item

        symbols = None
        input_dict = CommentedMap()

        if 'default' in kwargs:
            input_dict['default'] = kwargs.pop('default')
        if 'label' in kwargs:
            input_dict['label'] = kwargs.pop('label')
        if 'symbols' in kwargs:
            symbols = kwargs.pop('symbols')

        name, input_type = _get_item(kwargs)

        if input_type == 'enum':
            typ = CommentedMap()
            typ['type'] = 'enum'
            # make sure symbols is set
            if symbols is None:
                raise ValueError("Please specify the enum's symbols.")
            # make sure symbols is not empty
            if symbols == []:
                raise ValueError("The enum's symbols cannot be empty.")
            # make sure the symbols are a list
            if type(symbols) != list:
                raise ValueError('Symbols should be a list.')
            # make sure symbols is a list of strings
            symbols = [str(s) for s in symbols]

            typ['symbols'] = symbols
            input_dict['type'] = typ
        else:
            # Set the 'type' if we can't use simple notation (because there is
            # a default value or a label)
            if bool(input_dict):
                input_dict['type'] = input_type

        msg = '"{}" is already used as a workflow input. Please use a ' +\
              'different name.'
        if name in self.wf_inputs:
            raise ValueError(msg.format(name))

        # Add 'type' for complex input types, so the user doesn't have to do it
        if isinstance(input_type, dict):
            input_dict['type'] = input_type

        # Make sure we can use the notation without 'type' if the input allows
        # it.
        if bool(input_dict):
            self.wf_inputs[name] = input_dict
        else:
            self.wf_inputs[name] = input_type

        return Reference(input_name=name)

    def add_outputs(self, **kwargs):
        """Add workflow outputs.

        The output type is added automatically, based on the steps in the steps
        library.

        Args:
            kwargs (dict): A dict containing ``name=source name`` pairs.
                ``name`` is the name of the workflow output (e.g.,
                ``txt_files``) and source name is the name of the step that
                produced this output plus the output name (e.g.,
                ``saf-to-txt/out_files``).
        """
        self._closed()

        for name, source_name in kwargs.items():
            obj = {}
            obj['outputSource'] = source_name
            obj['type'] = self.step_output_types[source_name]
            self.wf_outputs[name] = obj

    def set_documentation(self, doc):
        """Set workflow documentation.

        Args:
            doc (str): documentation string.
        """
        self._closed()

        self.documentation = doc

    def set_label(self, label):
        """Set workflow label.

        Args:
            label (str): short description of workflow.
        """
        self._closed()

        self.label = label

    def _get_step(self, name, make_copy=True):
        """Return step from steps library.

        Optionally, the step returned is a deep copy from the step in the steps
        library, so additional information (e.g., about whether the step was
        scattered) can be stored in the copy.

        Args:
            name (str): name of the step in the steps library.
            make_copy (bool): whether a deep copy of the step should be
                returned or not (default: True).

        Returns:
            Step from steps library.

        Raises:
            ValueError: The requested step cannot be found in the steps
                library.
        """
        self._closed()

        s = self.steps_library.get_step(name)
        if s is None:
            msg = '"{}" not found in steps library. Please check your ' \
                  'spelling or load additional steps'
            raise ValueError(msg.format(name))
        if make_copy:
            s = copy.deepcopy(s)
        return s

    def _generate_step_name(self, step_name):
        name = step_name
        i = 1

        while name in self.steps_library.step_ids:
            name = '{}-{}'.format(step_name, i)
            i += 1

        return name

    def to_obj(self, wd=False, pack=False, relpath=None):
        """Return the created workflow as a dict.

        The dict can be written to a yaml file.

        Returns:
            A yaml-compatible dict representing the workflow.
        """
        self._closed()

        obj = CommentedMap()
        obj['cwlVersion'] = 'v1.0'
        obj['class'] = 'Workflow'
        try:
            obj['doc'] = self.documentation
        except (AttributeError, ValueError):
            pass
        try:
            obj['label'] = self.label
        except (AttributeError, ValueError):
            pass
        if self._has_requirements():
            obj['requirements'] = []
        if self.has_workflow_step:
            obj['requirements'].append(
                {'class': 'SubworkflowFeatureRequirement'})
        if self.has_scatter_requirement:
            obj['requirements'].append({'class': 'ScatterFeatureRequirement'})
        if self.has_multiple_inputs:
            obj['requirements'].append(
                {'class': 'MultipleInputFeatureRequirement'})
        obj['inputs'] = self.wf_inputs
        obj['outputs'] = self.wf_outputs

        steps_obj = CommentedMap()
        for key in self.wf_steps:
            steps_obj[key] = self.wf_steps[key].to_obj(relpath=relpath,
                                                       pack=pack,
                                                       wd=wd)
        obj['steps'] = steps_obj

        return obj

    def to_script(self, wf_name='wf'):
        """Generated and print the scriptcwl script for the currunt workflow.

        Args:
            wf_name (str): string used for the WorkflowGenerator object in the
                generated script (default: ``wf``).
        """
        self._closed()

        script = []

        # Workflow documentation
        # if self.documentation:
        #    if is_multiline(self.documentation):
        #        print('doc = """')
        #        print(self.documentation)
        #        print('"""')
        #        print('{}.set_documentation(doc)'.format(wf_name))
        #    else:
        #        print('{}.set_documentation(\'{}\')'.format(wf_name,
        #        self.documentation))

        # Workflow inputs
        params = []
        returns = []
        for name, typ in self.wf_inputs.items():
            params.append('{}=\'{}\''.format(name, typ))
            returns.append(name)
        script.append('{} = {}.add_inputs({})'.format(
            ', '.join(returns), wf_name, ', '.join(params)))

        # Workflow steps
        returns = []
        for name, step in self.wf_steps.items():
            pyname = step.python_name
            returns = ['{}_{}'.format(pyname, o) for o in step['out']]
            params = ['{}={}'.format(name, python_name(param))
                      for name, param in step['in'].items()]
            script.append('{} = {}.{}({})'.format(
                ', '.join(returns), wf_name, pyname, ', '.join(params)))

        # Workflow outputs
        params = []
        for name, details in self.wf_outputs.items():
            params.append('{}={}'.format(
                name, python_name(details['outputSource'])))
        script.append('{}.add_outputs({})'.format(wf_name, ', '.join(params)))

        return '\n'.join(script)

    @staticmethod
    def _get_input_type(step, input_name):
        input_type = step.input_types.get(input_name)
        if not input_type:
            input_type = step.optional_input_types[input_name]

        if step.is_scattered:
            for scattered_input in step.scattered_inputs:
                if scattered_input == input_name:
                    input_type += '[]'

        return input_type

    def _get_source_type(self, ref):
        if isinstance(ref, list):
            self.has_multiple_inputs = True
            return [self._get_source_type_single(r) for r in ref]
        else:
            return self._get_source_type_single(ref)

    def _get_source_type_single(self, ref):
        if ref.refers_to_step_output():
            step = self.wf_steps[ref.step_name]
            return step.output_types[ref.output_name]
        else:
            input_def = self.wf_inputs[ref.input_name]
            if isinstance(input_def, six.string_types):
                return input_def
            return input_def['type']

    @staticmethod
    def _types_match(type1, type2):
        """Returns False only if it can show that no value of type1
        can possibly match type2.

        Supports only a limited selection of types.
        """
        if isinstance(type1, six.string_types) and \
                isinstance(type2, six.string_types):
            type1 = type1.rstrip('?')
            type2 = type2.rstrip('?')
            if type1 != type2:
                return False

        return True

    def _type_check_reference(self, step, input_name, reference):
        input_type = self._get_input_type(step, input_name)
        source_type = self._get_source_type(reference)
        if isinstance(source_type, list):
            # all source_types must be equal
            if len(set(source_type)) > 1:
                inputs = ['{} ({})'.format(n, t)
                          for n, t in zip(reference, source_type)]
                msg = 'The types of the workflow inputs/step outputs for ' \
                      '"{}" are not equal: {}.'.format(input_name,
                                                       ', '.join(inputs))
                raise ValueError(msg)

            # continue type checking using the first item from the list
            source_type = source_type[0]
            input_type = input_type['items']
            reference = reference[0]

        if self._types_match(source_type, input_type):
            return True
        else:
            if step.is_scattered:
                scattered = ' (scattered)'
            else:
                scattered = ''
            if reference.refers_to_wf_input():
                msg = 'Workflow input "{}" of type "{}" is not'
                msg += ' compatible with{} step input "{}" of type "{}"'
                msg = msg.format(
                        reference.input_name, source_type,
                        scattered,
                        python_name(input_name), input_type)
            else:
                msg = 'Step output "{}" of type "{}" is not'
                msg += ' compatible with{} step input "{}" of type "{}"'
                msg = msg.format(
                        reference, source_type,
                        scattered,
                        python_name(input_name), input_type)
            raise ValueError(msg)

    def _make_step(self, step, **kwargs):
        self._closed()

        for k in step.get_input_names():
            p_name = python_name(k)
            if p_name in kwargs.keys():
                if isinstance(kwargs[p_name], Reference):
                    step.set_input(p_name, six.text_type(kwargs[p_name]))
                elif isinstance(kwargs[p_name], list):
                    if all(isinstance(n, Reference) for n in kwargs[p_name]):
                        step.set_input(p_name, kwargs[k])
                    else:
                        raise ValueError(
                            'List of inputs contains an input with an '
                            'incorrect type for keyword argument {} (should '
                            'be a value returned by set_input or from adding '
                            'a step).'.format(p_name))
                else:
                    raise ValueError(
                        'Incorrect type (should be a value returned'
                        'by set_inputs() or from adding a step) for keyword '
                        'argument {}'.format(p_name))
            elif k not in step.optional_input_names:
                raise ValueError(
                    'Expecting "{}" as a keyword argument.'.format(p_name))

        if 'scatter' in kwargs.keys() or 'scatter_method' in kwargs.keys():
            # Check whether 'scatter' keyword is present
            if not kwargs.get('scatter'):
                raise ValueError('Expecting "scatter" as a keyword argument.')

            # Check whether the scatter variables are valid for this step
            scatter_vars = kwargs.get('scatter')
            if isinstance(scatter_vars, six.string_types):
                scatter_vars = [scatter_vars]

            for var in scatter_vars:
                if var not in step.get_input_names():
                    msg = 'Invalid variable "{}" for scatter.'
                    raise ValueError(msg.format(var))
                step.scattered_inputs.append(var)

            # Check whether 'scatter_method' keyword is present if there is
            # more than 1 scatter variable
            if not kwargs.get('scatter_method') and len(scatter_vars) > 1:
                msg = 'Expecting "scatter_method" as a keyword argument.'
                raise ValueError(msg)

            # Check validity of scatterMethod
            scatter_methods = ['dotproduct', 'nested_crossproduct',
                               'flat_crossproduct']
            m = kwargs.get('scatter_method')
            if m and m not in scatter_methods:
                msg = 'Invalid scatterMethod "{}". Please use one of ({}).'
                raise ValueError(msg.format(m, ', '.join(scatter_methods)))
            step.scatter_method = m

            # Update step output types (outputs are now arrays)
            for name, typ in step.output_types.items():
                step.output_types[name] = {'type': 'array', 'items': typ}

            self.has_scatter_requirement = True
            step.is_scattered = True

        # Check types of references
        for k in step.get_input_names():
            p_name = python_name(k)
            if p_name in kwargs.keys():
                self._type_check_reference(step, k, kwargs[p_name])

        # Make sure the step has a unique name in the workflow (so command line
        # tools can be added to the same workflow multiple times).
        name_in_wf = self._generate_step_name(step.name)
        step._set_name_in_workflow(name_in_wf)
        self.steps_library.step_ids.append(name_in_wf)

        # Create a reference for each output for use in subsequent
        # steps' inputs.
        outputs = []
        for n in step.output_names:
            ref = step.output_reference(n)
            self.step_output_types[ref] = step.output_types[n]
            outputs.append(ref)

        self._add_step(step)

        if len(outputs) == 1:
            return outputs[0]
        return outputs

    def validate(self):
        """Validate workflow object.

        This method currently validates the workflow object with the use of
        cwltool. It writes the workflow to a tmp CWL file, reads it, validates
        it and removes the tmp file again. By default, the workflow is written
        to file using absolute paths to the steps.
        """
        # define tmpfile
        (fd, tmpfile) = tempfile.mkstemp()
        os.close(fd)
        try:
            # save workflow object to tmpfile,
            # do not recursively call validate function
            self.save(tmpfile, mode='abs', validate=False)
            # load workflow from tmpfile
            document_loader, processobj, metadata, uri = load_cwl(tmpfile)
        finally:
            # cleanup tmpfile
            os.remove(tmpfile)

    def _pack(self, fname, encoding):
        """Save workflow with ``--pack`` option

        This means that al tools and subworkflows are included in the workflow
        file that is created. A packed workflow cannot be loaded and used in
        scriptcwl.
        """
        (fd, tmpfile) = tempfile.mkstemp()
        os.close(fd)
        try:
            self.save(tmpfile, mode='abs', validate=False)
            document_loader, processobj, metadata, uri = load_cwl(tmpfile)
        finally:
            # cleanup tmpfile
            os.remove(tmpfile)

        with codecs.open(fname, 'wb', encoding=encoding) as f:
            f.write(print_pack(document_loader, processobj, uri, metadata))

    def save(self, fname, mode=None, validate=True, encoding='utf-8',
             wd=False, inline=False, relative=False, pack=False):
        """Save the workflow to file.

        Save the workflow to a CWL file that can be run with a CWL runner.

        Args:
            fname (str): file to save the workflow to.
            mode (str): one of  (rel, abs, wd, inline, pack)
            encoding (str): file encoding to use (default: ``utf-8``).
        """
        self._closed()

        if mode is None:
            mode = 'abs'
            if pack:
                mode = 'pack'
            elif wd:
                mode = 'wd'
            elif relative:
                mode = 'rel'

            msg = 'Using deprecated save method. Please save the workflow ' \
                  'with: wf.save(\'{}\', mode=\'{}\'). Redirecting to new ' \
                  'save method.'.format(fname, mode)
            warnings.warn(msg, DeprecationWarning)

        modes = ('rel', 'abs', 'wd', 'inline', 'pack')
        if mode not in modes:
            msg = 'Illegal mode "{}". Choose one of ({}).'\
                  .format(mode, ','.join(modes))
            raise ValueError(msg)

        if validate:
            self.validate()

        dirname = os.path.dirname(os.path.abspath(fname))
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        if mode == 'inline':
            msg = ('Inline saving is deprecated. Please save the workflow '
                   'using mode=\'pack\'. Setting mode to pack.')
            warnings.warn(msg, DeprecationWarning)
            mode = 'pack'

        if mode == 'rel':
            relpath = dirname
            save_yaml(fname=fname, wf=self, pack=False, relpath=relpath,
                      wd=False)

        if mode == 'abs':
            save_yaml(fname=fname, wf=self, pack=False, relpath=None,
                      wd=False)

        if mode == 'pack':
            self._pack(fname, encoding)

        if mode == 'wd':
            if self.get_working_dir() is None:
                raise ValueError('Working directory not set.')
            else:
                # save in working_dir
                bn = os.path.basename(fname)
                wd_file = os.path.join(self.working_dir, bn)
                save_yaml(fname=wd_file, wf=self, pack=False, relpath=None,
                          wd=True)
                # and copy workflow file to other location (as though all steps
                # are in the same directory as the workflow)
                try:
                    shutil.copy2(wd_file, fname)
                except shutil.Error:
                    pass

    def get_working_dir(self):
        return self.working_dir

    def add_inputs(self, **kwargs):
        """Deprecated function, use add_input(self, **kwargs) instead.
        Add workflow input.

        Args:
            kwargs (dict): A dict with a `name: type` item
                and optionally a `default: value` item, where name is the
                name (id) of the workflow input (e.g., `dir_in`) and type is
                the type of the input (e.g., `'Directory'`).
                The type of input parameter can be learned from
                `step.inputs(step_name=input_name)`.

        Returns:
            inputname

        Raises:
            ValueError: No or multiple parameter(s) have been specified.
        """
        msg = ('The add_inputs() function is deprecation in favour of the '
               'add_input() function, redirecting...')
        warnings.warn(msg, DeprecationWarning)
        return self.add_input(**kwargs)
