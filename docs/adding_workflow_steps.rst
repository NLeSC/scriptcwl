Adding workflow steps
=====================

After loading steps and adding workflow inputs, the steps of the workflow should
be specified. To add a step to a workflow, its method must
be called on the ``WorkflowGenerator`` object. For example, to add a step
called ``add`` [#]_ to the workflow, the following method must be called:
::

  answer1 = wf.add(x=num1, y=num2)

The method expects a list of ``key=value`` pairs as input parameters. (To find
out what inputs a step needs call ``wf.inputs(<step name>)``. This method prints
all inputs and their types.) ``wf.<step name>()`` returns a list of strings containing output
names that can be used as input for later steps, or that can be connected
to workflow outputs. For example, in a later step, ``answer1`` can be used as input:
::

  answer2 = wf.multiply(x=answer1, y=num2)

Scattering steps
################

Scriptcwl supports `scattering steps <http://www.commonwl.org/v1.0/Workflow.html#WorkflowStep>`_.
To scatter a step, keyword arguments
``scatter`` and ``scatter_method`` must be provided when a step is added to the
workflow. To scatter a step called ``echo``, which has a single input argument
``message``, this would look like:
::

	output = wf.echo(message=input1, scatter='message', scatter_method='dotproduct')

The type of ``message``, should be array (e.g., an array of strings).

To scatter over multiple variables, ``scatter`` also accepts a list of input names:
::

	output = wf.echo(message1=input1, message2=input2, scatter=['message1', 'message2'], scatter_method='dotproduct')

.. [#] Scriptcwl contains two example command line tools, ``add`` and ``multiply``. The Python and CWL files can be found in the `examples folder <https://github.com/NLeSC/scriptcwl/tree/master/scriptcwl/examples>`_.
