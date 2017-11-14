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
