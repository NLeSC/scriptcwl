Adding workflow documentation
==============================

To add documentation to your workflow, use the ``set_documentation()`` method:
::

	doc = """Workflow that performs a special calculation with two numbers

	The two numbers are added and the answer is multiplied by the second number.

	Input:
		num1: int
		num2: int

	Output:
		answer: int
	"""
	wf.set_documentation(doc)
