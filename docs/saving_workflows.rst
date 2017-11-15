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

By default, the paths to the workflow steps are
If, for some reason, you want to save the workflow with absolute paths,


Embedding steps in the workflow
###############################

It is also possible to embed the workflow steps in the workflow. You can do this
by saving the workflow with the ``inline=True`` option:
::
	wf.save('workflow.cwl', inline=True)

(This is similar to the ``--pack`` option of ``cwltool``, but the result is slightly more human readable.)
With ``inline`` set to ``True``, the example workflow looks like:
::

  To be added.

Workflow validation
###################

Before the workflow is saved, it is validated using ``cwltool``. Validation can also be
triggered manually:
::

	wf.validate()
