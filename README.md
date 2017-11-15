# scriptcwl

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/8f383bca18384d8187c10c27affa9d53)](https://www.codacy.com/app/j-vanderzwaan/scriptcwl?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=NLeSC/scriptcwl&amp;utm_campaign=Badge_Grade)
[![Codacy Badge](https://api.codacy.com/project/badge/Coverage/8f383bca18384d8187c10c27affa9d53)](https://www.codacy.com/app/j-vanderzwaan/scriptcwl?utm_source=github.com&utm_medium=referral&utm_content=NLeSC/scriptcwl&utm_campaign=Badge_Coverage)
[![Build Status](https://travis-ci.org/NLeSC/scriptcwl.svg?branch=master)](https://travis-ci.org/NLeSC/scriptcwl)
[![Documentation Status](https://readthedocs.org/projects/scriptcwl/badge/?version=latest)](http://scriptcwl.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/scriptcwl.svg)](https://badge.fury.io/py/scriptcwl)
[![PyPI](https://img.shields.io/pypi/pyversions/scriptcwl.svg)](https://pypi.python.org/pypi/scriptcwl)


scriptcwl is a Python package for creating workflows in
[common workflow language](http://www.commonwl.org/). If you give it a number of CWL
`CommandLineTool`s, you can create a workflow by writing a Python script. This can
be done interactively using [Jupyter Notebooks](http://jupyter.org/). More information
about using scriptcwl can be found in the [documentation](http://scriptcwl.readthedocs.io/en/latest/).

```python
from scriptcwl import WorkflowGenerator

with WorkflowGenerator() as wf:
    wf.load(steps_dir='/path_to_scriptcwl/scriptcwl/examples/')

    num1 = wf.add_input(num1='int')
    num2 = wf.add_input(num2='int')

    answer1 = wf.add(x=num1, y=num2)
    answer2 = wf.multiply(x=answer1, y=num2)

    wf.add_outputs(final_answer=answer2)

    wf.save('add_multiply_example_workflow.cwl')
```

This workflow has two integers as inputs (``num1`` and ``num2``), and first adds
these two numbers (``wf.add(x=num1, y=num2)``), and then multiplies the answer
with the second input (``num2``). The result of that processing step is the output
of the workflow. Finally, the workflow is saved to a file. The result looks like:

```
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
```

The Python and CWL files used in the example can be found in the [examples folder](https://github.com/NLeSC/scriptcwl/tree/master/scriptcwl/examples).

## Installation

Install using pip:

```
pip install scriptcwl
```

For development:

```
git clone git@github.com:NLeSC/scriptcwl.git
cd scriptcwl
git checkout develop
pip install -r requirements.txt
python setup.py develop
```

Run tests (including coverage) with:
```
python setup.py develop test
```

## Useful tools

To use scriptcwl for creating CWL workflows, you need CWL `CommandLineTool`s.
There are some software packages that help with generating those
for existing command line tools written in Python:

* [argparse2tool](https://github.com/erasche/argparse2tool#cwl-specific-functionality): Generate CWL CommandLineTool wrappers (and/or Galaxy tool descriptions) from Python programs that use argparse. Also supports the [click](http://click.pocoo.org) argument parser.
* [pypi2cwl](https://github.com/common-workflow-language/pypi2cwl): Automatically run argparse2cwl on any package in PyPi.
* [python-cwlgen](https://github.com/common-workflow-language/python-cwlgen): Generate CommandLineTool and DockerRequirement programmatically
