Workflow inputs
===============

Wokflow inputs can be added by calling ``add_input()``:
::

	num1 = wf.add_input(num1='int')
	num2 = wf.add_input(num2='int')

The ``add_input()`` method expects a ``name=type`` pair as input parameter.
The pair connects an input name (``num1`` in the example) to a CWL type
(``'int'``). An overview of CWL types can be found in the
`specification <http://www.commonwl.org/v1.0/Workflow.html#CWLType>`_.

Optional inputs
###############

Workflow inputs can be made optional by adding a questionmark to the type:
::

	num1 = wf.add_input(num1='int?')

Default values
##############

When adding an input parameter to a workflow, you can set a default value:
::

	num1 = wf.add_input(num1='int', default=5)

As a consequence, ``default`` cannot be used as a name for a workflow input parameter.

Labels
######

You can also add a label to a workflow input:
::

	num1 = wf.add_input(num1='int', label='The first number that is processed.')

Again, this means ``label`` cannot be used as a name for a workflow input parameter.
