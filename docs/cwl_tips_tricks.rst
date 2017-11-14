CWL Tips and Tricks
===================

Generate yaml file with workflow inputs
#######################################

You can use ``cwltool --make-template`` to generate a yaml file with all the workflow inputs:
::

	cwltool --make-template add_multiply_example.cwl > inputs.yml

``inputs.yml`` contains:
::

	num1: 0
	num2: 0

Use your favorite text editor to set the inputs to appropriate values. Save the
file, and use it as input for your workflow:
::

cwltool add_multiply_example.cwl inputs.yml

Using cwl-runner
################

Install the ``cwlref-runner`` package to set ``cwl-runner`` to ``cwltool``:
::

 	pip install cwlref-runner

If ``cwl-runner`` is set, you can run workflows by typing:
::

	chmod +x workflow.cwl
	./workflow.cwl <arguments>

If you have other CWL implementations installed and want ``cwl-runner`` to use one
of these implementations, you should define a symlink that points to the implementation
you want to use; e.g., by manually creating a symlink and adding it to your ``$PATH``
variable, or by using the linux `alternatives <https://linux.die.net/man/8/update-alternatives>`_ system.
