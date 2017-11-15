Saving workflows
================

To save a workflow call the ``WorkflowGenerator.save()`` method:
::

  wf.save('workflow.cwl')

By default, the encoding used to save the workflow is ``utf-8``. If necessary,
a different encoding can be specified:
::

  wf.save('workflow.cwl', encoding='utf-16')

Saving workflows with absolute paths
####################################

By default, the paths in the ``run`` field of workflow steps are relative to the
location where the workflow is saved. If, for some reason, you want to save
the workflow with absolute paths, use the ``relative=False`` option:
::

  wf.save('workflow.cwl', relative=False)


Embedding steps in the workflow
###############################

It is also possible to embed the workflow steps in the workflow. You can do this
by saving the workflow with the ``inline=True`` option:
::
	wf.save('workflow.cwl', inline=True)

(This is similar to the ``--pack`` option of ``cwltool``, but the result is slightly more human readable.)

With ``inline`` set to ``True``, the example workflow looks like:
::

  #!/usr/bin/env cwl-runner
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
      run:
        cwlVersion: v1.0
        class: CommandLineTool
        baseCommand: [python, -m, scriptcwl.examples.add]

        inputs:
        - type: int
          inputBinding:
            position: 1
          id: _:add.cwl#x
        - type: int
          inputBinding:
            position: 2

          id: _:add.cwl#y
        stdout: cwl.output.json

        outputs:
        - type: int
          id: _:add.cwl#answer
        id: _:add.cwl
      in:
        y: num2
        x: num1
      out:
      - answer
    multiply:
      run:
        cwlVersion: v1.0
        class: CommandLineTool
        baseCommand: [python, -m, scriptcwl.examples.multiply]

        inputs:
        - type: int
          inputBinding:
            position: 1
          id: _:multiply.cwl#x
        - type: int
          inputBinding:
            position: 2

          id: _:multiply.cwl#y
        stdout: cwl.output.json

        outputs:
        - type: int
          id: _:multiply.cwl#answer
        id: _:multiply.cwl
      in:
        y: num2
        x: add/answer
      out:
      - answer

Workflow validation
###################

Before the workflow is saved, it is validated using ``cwltool``. Validation can also be
triggered manually:
::

	wf.validate()
