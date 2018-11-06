Printing workflows
==================

To view its contents, a workflow can be printed at any time:

.. code-block:: python

  with scriptcwl.WorkflowGenerator() as wf:
    print(wf)

For an empty workflow, this looks like:

.. code-block:: none

  #!/usr/bin/env cwl-runner
  cwlVersion: v1.0
  class: Workflow
  inputs: {}
  outputs: {}
  steps: {}

In a printed workflow, steps are referred to by their absolute paths.
**Therefore, do not use this method for saving workflows.
The absolute paths make them unportable.**
