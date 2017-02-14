from ruamel import yaml
import os
import codecs
import six
import copy

from functools import partial

from .scriptcwl import load_steps
from .step import Step, python_name
from .yamlmultiline import str_presenter, is_multiline


class WorkflowGenerator(object):
    """Class for creating a CWL workflow.

    The WorkflowGenerator class allows users to tie together inputs and outputs
    of the steps that need to be executed to perform a data processing task.
    The steps (i.e., command line tools and subworkflows) must be added to the
    steps library of the WorkflowGenerator object before they can be added to
    the workflow. To add steps to the steps library, the `load` method can be
    called with either a path to a directory containing CWL files:

    ```
    from scriptcwl import WorkflowGenerator

    wf = WorkflowGenerator()
    wf.load(steps_dir='/path/to/dir/with/cwl/steps/')
    ```

    Or a single CWL file:

    ```
    wf.load(step_file='/path/to/cwl/step/file')
    ```

    `wf.load` can be called multiple times. Step files are added to the steps
    library one after the other. For every step that is added to the steps
    library, a method with the same name is added to the WorkflowGenerator
    object. To add a step to the workflow, this method must be called (examples
    below).

    Next, the user should add one or more workflow inputs:

    ```
    txt_dir = wf.add_inputs(txt_dir='Directory')
    ```

    The `add_inputs` method expects (key, value) pairs as input parameters.
    Each pair connects an input name (`txt_dir` in the example) to a type
    (`'Directory'`).

    `addd_inputs` method returns a list of strings containing the names that
    can be used to connect these input parameters to step input parameter
    names. (Please note that because **kwargs are unordered, the list of input
    names may not be in the same order as the **kwargs. When a workflow has
    multiple inputs, it is probably safer to call `add_inputs` for every
    parameter separately.)

    Next, workflow steps can be added. To add a workflow step, its method must
    be called on the WorkflowGenerator object. This method expects a list of
    (key, value) pairs as input parameters. (To find out what inputs a step
    needs call `wf.inputs(<step name>)`. This method prints all the inputs and
    their types.) The method returns a list of strings containing output names
    that can be used as input for later steps, or that can be connected to
    workflow outputs.

    For example, to add a step called `frog-dir` to the workflow, the following
    method must be called:

    ```
    frogout = wf.frog_dir(dir_in=txt_dir)
    ```

    In a next step, `frogout` can be used as input:

    ```
    saf = wf.frog_to_saf(in_files=frogout)
    txt = wf.saf_to_txt(in_files=saf)
    ```

    Etcetera.

    When all steps of the workflow have been added, the user can specify
    workflow outputs:

    ```
    wf.add_outputs(txt=txt)
    ```

    Finally, the workflow can be saved to file:

    ```
    wf.save('workflow.cwl')
    ```

    To list steps and signatures available in the steps library, call:

    ```
    wf.list_steps()
    ```
    """

    def __init__(self, steps_dir=None):
        self.wf_steps = {}
        self.wf_inputs = {}
        self.wf_outputs = {}
        self.step_output_types = {}
        self.steps_library = {}
        self.has_workflow_step = False
        self.has_scatter_requirement = False

        self.load(steps_dir)

    def __getattr__(self, name, **kwargs):
        name = cwl_name(name)
        step = self._get_step(name)
        return partial(self._make_step, step, **kwargs)

    def load(self, steps_dir=None, step_file=None):
        """Load CWL steps into the WorkflowGenerator's steps library.

        Adds steps (command line tools and workflows) to the
        WorkflowGenerator's steps library. These steps can be used to create
        workflows.

        Args:
            steps_dir (str): path to directory containing CWL files. All CWL in
                the directory are loaded.
            step_file (str): path to a file containing a CWL step that will be
                added to the steps library.
        """
        steps = load_steps(steps_dir=steps_dir, step_file=step_file)
        for n, step in steps.iteritems():
            if n in self.steps_library.keys():
                print 'WARNING: step "{}" already in steps library'.format(n)
            else:
                self.steps_library[n] = step

    def list_steps(self):
        """Prints the signature of all steps in the steps library.
        """
        for name, step in self.steps_library.iteritems():
            print 'Step "{}": {}'.format(name, step)

    def _has_requirements(self):
        """Returns True if the workflow needs a requirements section.

        Returns:
            bool: True if the workflow needs a requirements section, False
                otherwise.
        """
        return bool(self.has_workflow_step or self.has_scatter_requirement)

    def inputs(self, name):
        """List input names and types of a step in the steps library.

        Args:
            name (str): name of a step in the steps library.
        """
        s = self._get_step(name, make_copy=False)
        print s.list_inputs()

    def _add_step(self, step):
        """Add a step to the workflow.

        Args:
            step (Step): a step from the steps library.
        """
        self.has_workflow_step = self.has_workflow_step or step.is_workflow
        self.wf_steps[step.name] = step.to_obj()

    def add_inputs(self, **kwargs):
        """Add workflow inputs.

        Args:
            kwargs (dict): A dict with `name=type` pairs, where name is the
                name (id) of the workflow input (e.g., `dir_in`) and type is
                the type of the input (e.g., `'Directory'`). The type of input
                parameters can be learned from
                `step.inputs(step_name=input_name)`.

        Returns:
            list of inputnames
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

        The output type is added automatically, based on the steps in the steps
        library.

        Args:
            kwargs (dict): A dict containing name=source name pairs. name is
                the name of the workflow output (e.g., `txt_files`) and source
                name is the name of the step that produced this output plus the
                output name (e.g., `saf-to-txt/out_files`).
        """
        for name, source_name in kwargs.iteritems():
            obj = {}
            obj['outputSource'] = source_name
            obj['type'] = self.step_output_types[source_name]
            self.wf_outputs[name] = obj

    def set_documentation(self, doc):
        """Set workflow documentation.

        Args:
            doc (str): documentation string.
        """
        self.documentation = doc

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
        s = self.steps_library.get(name)
        if s is None:
            msg = '"{}" not found in steps library. Please check your ' \
                  'spelling or load additional steps'
            raise ValueError(msg.format(name))
        if make_copy:
            s = copy.deepcopy(s)
        return s

    def to_obj(self):
        """Return the created workflow as a dict.

        The dict can be written to a yaml file.

        Returns:
            A yaml-compatible dict representing the workflow.
        """
        obj = {}
        obj['cwlVersion'] = 'v1.0'
        obj['class'] = 'Workflow'
        try:
            obj['doc'] = self.documentation
        except (AttributeError, ValueError):
            pass
        if self._has_requirements():
            obj['requirements'] = []
        if self.has_workflow_step:
            obj['requirements'].append({'class': 'SubworkflowFeatureRequirement'})
        if self.has_scatter_requirement:
            obj['requirements'].append({'class': 'ScatterFeatureRequirement'})
        obj['inputs'] = self.wf_inputs
        obj['outputs'] = self.wf_outputs
        obj['steps'] = self.wf_steps
        return obj

    def to_script(self, wf_name='wf'):
        """Generated and print the scriptcwl script for the currunt workflow.

        Args:
            wf_name (str): string used for the WorkflowGenerator object in the
                generated script (default: wf).
        """

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

        if 'scatter' in kwargs.keys() or 'scatter_method' in kwargs.keys():
            # Check whether both required keyword arguments are present
            msg = 'Expecting "{}" as a keyword argument.'
            if not kwargs.get('scatter'):
                raise ValueError(msg.format('scatter'))
            if not kwargs.get('scatter_method'):
                raise ValueError(msg.format('scatter_method'))

            # Check validity of scatterMethod
            scatter_methods = ['dotproduct', 'nested_crossproduct',
                               'flat_crossproduct']
            m = kwargs.get('scatter_method')
            if m not in scatter_methods:
                msg = 'Invalid scatterMethod "{}". Please use one of ({}).'
                raise ValueError(msg.format(m, ', '.join(scatter_methods)))
            step.scatter_method = m

            # Check whether the scatter variables are valid for this step
            scatter_vars = kwargs.get('scatter')
            if isinstance(scatter_vars, six.string_types):
                scatter_vars = [scatter_vars]

            for var in scatter_vars:
                if var not in step.get_input_names():
                    msg = 'Invalid variable "{}" for scatter.'
                    raise ValueError(msg.format(var))
                step.scattered_inputs.append(var)

            # Update step output types (outputs are now arrays)
            for name, typ in step.step_outputs.iteritems():
                step.step_outputs[name] = {'type': 'array', 'items': typ}

            self.has_scatter_requirement = True
            step.is_scattered = True

        outputs = []
        for n in step.output_names:
            oname = step.output_to_input(n)
            self.step_output_types[oname] = step.step_outputs[n]
            outputs.append(step.output_to_input(n))

        self._add_step(step)

        if len(outputs) == 1:
            return outputs[0]
        return outputs

    def save(self, fname, encoding='utf-8'):
        """Save the workflow to file.

        Save the workflow to a CWL file that can be run with a CWL runner.

        Args:
            fname (str): file to save the workflow to.
            encoding (str): file encoding to use (default: utf-8).
        """
        dirname = os.path.dirname(os.path.abspath(fname))

        if not os.path.exists(dirname):
            os.makedirs(dirname)

        yaml.add_representer(str, str_presenter)
        with codecs.open(fname, 'wb', encoding=encoding) as yaml_file:
            yaml_file.write('#!/usr/bin/env cwl-runner\n')
            yaml_file.write(yaml.dump(self.to_obj(), Dumper=yaml.RoundTripDumper))


def cwl_name(name):
    """Transform python name to cwl name.

    Args:
        name (str): string to transform.

    Returns:
        transformed string.
    """
    name = name.replace('_', '-')

    return name
