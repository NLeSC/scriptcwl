Loading steps
=============

Before you can create workflows with scriptcwl, you need to load processing steps
(i.e., ``CommandLineTools``, ``ExpressionTools`` and/or (sub) ``Workflows``).
To load a directory of .cwl files, type:
::

	from scriptcwl import WorkflowGenerator

	with WorkflowGenerator() as wf:
		wf.load(steps_dir='/path/to/dir/with/cwl/steps/')

To load a single cwl file, do:
::

	with WorkflowGenerator() as wf:
		wf.load(step_file='/path/to/workflow.cwl')

The path to the ``step_file`` can be a local file path or a url.

You can also load a list of step files and directories:
::

	al_my_steps = ['step.cwl', 'url.cwl', '/path/to/directory/']
	with WorkflowGenerator() as wf:
		wf.load(step_list=all_my_steps)

``wf.load()`` can be called multiple times. Step files are added to the
steps library one after the other. For every step that is added to the
steps library, a method with the same name is added to the
WorkflowGenerator object. To add a step to the workflow, this method must
be called (examples below).
