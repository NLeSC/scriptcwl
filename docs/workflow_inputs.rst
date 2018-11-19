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

Arrays and other complex input types
####################################

Arrays of workflow inputs can be specified with ``[]``:
::

  numbers = wf.add_input(numbers='int[]')

You can also specify the input using a dictionary with two keys: ``{'type':
'array', 'items': 'int'}``. In this case, it is necessary to wrap the array
declaration in a dictionary with a ``type`` key:
::

  array_of_ints = dict(type=dict(type='array', items='int'))
  numbers = wf.add_input(numbers=array_of_ints)

This way you also can specify more complex inputs. For example, to create an
array of arrays of strings, do:
::

  inp = dict(type=dict(type='array', items=dict(type='array', items='string')))
  strings = wf.add_input(my_array_of_array_of_strings=inp)

Use ``print(wf)`` and ``wf.validate()`` to make sure your inputs are correct.

Enums
#####

To use an enum as a workflow input, do:
::

	mode = wf.add_input(mode='enum', symbols=['one', 'two', 'three'])

The ``symbols`` should be a list of strings (lists containing other types are
converted lists of to strings).
Again, ``symbols`` cannot be used as a name for a workflow input parameter.
