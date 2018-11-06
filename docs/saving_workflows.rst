Saving workflows
================

To save a workflow call the ``WorkflowGenerator.save()`` method:
::

  wf.save('workflow.cwl')

By default, the paths in the ``run`` field of workflow steps are absolute. This means
that a workflow created on one machine cannot be run on another machine. However,
there are multiple options for creating portable workflows.

Saving workflows with relative paths
####################################

To get relative paths in the ``run`` field of workflow steps, use ``mode='rel'``:
::

  wf.save('workflow.cwl', mode='rel')

The paths in the ``run`` field are relative to where the workflow is saved. This
option is convenient when you are creating workflows using a single directory
with possible workflow steps.

Using a working directory
#########################

If you have multiple directories containing workflow steps and the locations of
these directories may differ depending on where software is installed (for example,
if you want to use the generic NLP steps from nlppln, but also need project specific
data processing steps), it is possible to specify a working directory when creating
the ``WorkflowGenerator`` object. If you this, all steps are copied to the working
directory. When you save the workflow using ``mode='wd'``, the paths in the ``run``
fields are set to the basename of the step (because all steps are in the same
directory).
::

  from scriptcwl import WorkflowGenerator

  with WorkflowGenerator(working_dir='path/to/working_dir') as wf:
    wf.load(steps_dir='some/path/')
    wf.load(steps_dir='some/other/path/')

    # add inputs, steps and outputs

    wf.save('workflow', mode='wd')

The workflow is saved in the working directory and then copied to
the specified location. To be able to run the workflow, use the copy in the
working directory (please note that the working directory is not deleted automatically).

Also, steps from urls are not copied to the working directory.

Pack workflows
##############

Another way to create workflows with all steps in one file is to save it with ``mode='pack'``:
::

  wf.save('workflow.cwl', mode='pack')

Please note that packed workflows cannot be used as a building block in ``scriptcwl``.
If you try to load a packed workflow, you will get a warning.

Saved With ``mode='pack'``, the example workflow looks like:
::

  {
      "cwlVersion": "v1.0",
      "$graph": [
          {
              "class": "CommandLineTool",
              "baseCommand": [
                  "python",
                  "-m",
                  "scriptcwl.examples.add"
              ],
              "inputs": [
                  {
                      "type": "int",
                      "inputBinding": {
                          "position": 1
                      },
                      "id": "#add.cwl/x"
                  },
                  {
                      "type": "int",
                      "inputBinding": {
                          "position": 2
                      },
                      "id": "#add.cwl/y"
                  }
              ],
              "stdout": "cwl.output.json",
              "outputs": [
                  {
                      "type": "int",
                      "id": "#add.cwl/answer"
                  }
              ],
              "id": "#add.cwl"
          },
          {
              "class": "CommandLineTool",
              "baseCommand": [
                  "python",
                  "-m",
                  "scriptcwl.examples.multiply"
              ],
              "inputs": [
                  {
                      "type": "int",
                      "inputBinding": {
                          "position": 1
                      },
                      "id": "#multiply.cwl/x"
                  },
                  {
                      "type": "int",
                      "inputBinding": {
                          "position": 2
                      },
                      "id": "#multiply.cwl/y"
                  }
              ],
              "stdout": "cwl.output.json",
              "outputs": [
                  {
                      "type": "int",
                      "id": "#multiply.cwl/answer"
                  }
              ],
              "id": "#multiply.cwl"
          },
          {
              "class": "Workflow",
              "inputs": [
                  {
                      "type": "int",
                      "id": "#main/num1"
                  },
                  {
                      "type": "int",
                      "id": "#main/num2"
                  }
              ],
              "outputs": [
                  {
                      "type": "int",
                      "outputSource": "#main/multiply-1/answer",
                      "id": "#main/final_answer"
                  }
              ],
              "steps": [
                  {
                      "run": "#add.cwl",
                      "in": [
                          {
                              "source": "#main/num1",
                              "id": "#main/add-1/x"
                          },
                          {
                              "source": "#main/num2",
                              "id": "#main/add-1/y"
                          }
                      ],
                      "out": [
                          "#main/add-1/answer"
                      ],
                      "id": "#main/add-1"
                  },
                  {
                      "run": "#multiply.cwl",
                      "in": [
                          {
                              "source": "#main/add-1/answer",
                              "id": "#main/multiply-1/x"
                          },
                          {
                              "source": "#main/num2",
                              "id": "#main/multiply-1/y"
                          }
                      ],
                      "out": [
                          "#main/multiply-1/answer"
                      ],
                      "id": "#main/multiply-1"
                  }
              ],
              "id": "#main"
          }
      ]
  }

Workflow validation
###################

Before the workflow is saved, it is validated using ``cwltool``. Validation can also be
triggered manually:
::

	wf.validate()

It is also possible to disable workflow validation on save:
::

  wf.save('workflow.cwl', validate=False)

File encoding
#############

By default, the encoding used to save workflows is ``utf-8``. If necessary,
a different encoding can be specified:
::

  wf.save('workflow.cwl', encoding='utf-16')
