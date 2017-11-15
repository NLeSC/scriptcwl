.. scriptcwl documentation master file, created by
   sphinx-quickstart on Mon Nov 13 15:12:14 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to the Scriptcwl Documentation!
=======================================

Scriptcwl is a Python package for creating `Common Workflow Language (CWL) <http://www.commonwl.org/>`_ workflows.
Given a number of CWL ``CommandLineTool``s, workflows can be created by writing a Python script, for example:
::

  from scriptcwl import WorkflowGenerator

  with WorkflowGenerator() as wf:
      wf.load(steps_dir='/path_to_scriptcwl/scriptcwl/examples/')

      num1 = wf.add_input(num1='int')
      num2 = wf.add_input(num2='int')

      answer1 = wf.add(x=num1, y=num2)
      answer2 = wf.multiply(x=answer1, y=num2)

      wf.add_outputs(final_answer=answer2)

      wf.save('add_multiply_example_workflow.cwl')

This workflow has two integers as inputs (``num1`` and ``num2``), and first adds
these two numbers (``wf.add(x=num1, y=num2)``), and then multiplies the answer
with the second input (``num2``). The result of that processing step is the output
of the workflow. Finally, the workflow is saved to a file. The result looks like:
::

  #!/usr/bin/env cwltool
  cwlVersion: v1.0
  class: Workflow
  inputs:
    num1: int
    num2: int
  outputs:
    final_answer:
      type: int
      outputSource: multiply/answer
  steps:
    add:
      run: add.cwl
      in:
        y: num2
        x: num1
      out:
      - answer
    multiply:
      run: multiply.cwl
      in:
        y: num2
        x: add/answer
      out:
      - answer

Loading processing steps
########################

``wf.load()`` can be called multiple times. Step files are added to the
steps library one after the other. For every step that is added to the
steps library, a method with the same name is added to the
WorkflowGenerator object. To add a step to the workflow, this method must
be called (examples below).



You can list the steps and workflows that are loaded into the WorkflowGenerator's steps library by typing:
::

  print(wf.list_steps())

For the example workflow, the output would be:
::

  Steps
  add...................... answer = wf.add(x, y)
  multiply................. answer = wf.multiply(x, y)

  Workflows

This means that there are two processing steps and no workflows loaded into the
steps library.

Workflow inputs
###############

Next, the user should add one or more workflow inputs:
::

  num1 = wf.add_input(num1='int')
  num2 = wf.add_input(num2='int')

The ``add_input()`` method expects a ``name=type`` pair as input parameter.
The pair connects an input name (``num1`` in the example) to a CWL type
(``'int'``). Optionally, a default value can be specified using
``default=value``.

The ``add_input()`` method returns a string containing the name
that can be used to connect this input parameter to step input parameter
names.

Adding processing steps
#######################

Next, workflow steps can be added. To add a workflow step, its method must
be called on the WorkflowGenerator object. This method expects a list of
``key=value`` pairs as input parameters. (To find out what inputs a step
needs call ``wf.inputs(<step name>)``. This method prints all the inputs
and their types.) The method returns a list of strings containing output
names that can be used as input for later steps, or that can be connected
to workflow outputs.

For example, to add a step called ``add`` to the workflow, the
following method must be called:
::

  answer1 = wf.add(x=num1, y=num2)

In a next step, ``answer1`` can be used as input:
::

  answer2 = wf.multiply(x=answer1, y=num2)

Specifying workflow outputs
###########################

When all steps of the workflow have been added, the user can specify
workflow outputs:
::

  wf.add_outputs(final_answer=answer2)

Finally, the workflow can be saved to file:
::

  wf.save('add_multiply_example_workflow.cwl')

Contents
========

.. toctree::
   :maxdepth: 2

   cwl_tips_tricks

API Reference
=============

.. toctree::
   :maxdepth: 2

   scriptcwl <apidocs/scriptcwl.rst>
