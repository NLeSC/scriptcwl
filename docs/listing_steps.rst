Listing steps
=============

Steps that are loaded into the WorkflowGenerator's steps library can be listed by running:
::

  print(wf.list_steps())

For the example workflow, the output would be:
::

  Steps
  add...................... answer = wf.add(x, y)
  multiply................. answer = wf.multiply(x, y)

  Workflows

This means that there are two processing steps and no (sub)workflows loaded into the
steps library. The listing contains the complete command to add the step to the workflow
(e.g., ``answer = wf.add(x, y)``). The command is supplied for convenient copy/pasting.
