# scriptcwl

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/8f383bca18384d8187c10c27affa9d53)](https://www.codacy.com/app/j-vanderzwaan/scriptcwl?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=NLeSC/scriptcwl&amp;utm_campaign=Badge_Grade)
[![Codacy Badge](https://api.codacy.com/project/badge/Coverage/8f383bca18384d8187c10c27affa9d53)](https://www.codacy.com/app/j-vanderzwaan/scriptcwl?utm_source=github.com&utm_medium=referral&utm_content=NLeSC/scriptcwl&utm_campaign=Badge_Coverage)
[![Build Status](https://travis-ci.org/NLeSC/scriptcwl.svg?branch=master)](https://travis-ci.org/NLeSC/scriptcwl)
[![PyPI version](https://badge.fury.io/py/scriptcwl.svg)](https://badge.fury.io/py/scriptcwl)
[![PyPI](https://img.shields.io/pypi/pyversions/scriptcwl.svg)](https://pypi.python.org/pypi/scriptcwl)


scriptcwl is a Python package to create workflows in
[common workflow language](http://www.commonwl.org/). If you give it a set of CWL
`CommandLineTool`s, you can create a workflow by writing a Python script. This can
be done interactively using [Jupyter Notebooks](http://jupyter.org/).

For example, to generate the [anonymize pipeline](https://github.com/WhatWorksWhenForWhom/nlppln/blob/develop/cwl/anonymize.cwl) (from the
[nlppln](https://github.com/WhatWorksWhenForWhom/nlppln) package), you'd have to write:

```python
import scriptcwl
from scriptcwl import WorkflowGenerator

wf = WorkflowGenerator()
wf.load(steps_dir='/path/to/dir/with/cwl/steps/')

doc = """Workflow that replaces named entities in text files.

Input:
  txt_dir: directory containing text files

Output:
  ner_stats: csv-file containing statistics about named entities in the text files
  txt: text files with named enities replaced
"""
wf.set_documentation(doc)

txt_dir = wf.add_inputs(txt_dir='Directory')

frogout = wf.frog_dir(dir_in=txt_dir)
saf = wf.frog_to_saf(in_files=frogout)
ner_stats = wf.save_ner_data(in_files=saf)
new_saf = wf.replace_ner(metadata=ner_stats, in_files=saf)
txt = wf.saf_to_txt(in_files=new_saf)

wf.add_outputs(ner_stats=ner_stats, txt=txt)

wf.save('anonymize.cwl')
```

When adding an input parameter to a workflow, you can set a default value:

```python
wf = WorkflowGenerator()
input1 = wf.add_inputs(input1='string', default='Hello world!')
```

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
pytest --cov
```

## Loading workflow steps

In order to be able to create workflows using `scriptcwl`, you need to provide
the `WorkflowGenerator` object with steps (i.e., `CommandLineTool`s,
`ExpressionTool`s and/or (sub)`Workflow`s). To load a directory of .cwl files, type:

```python
from scriptcwl import WorkflowGenerator

wf = WorkflowGenerator()
wf.load(steps_dir='/path/to/dir/with/cwl/steps/')
```

To load a single cwl file, do:
```python
wf.load(step_file='/path/to/workflow.cwl')
```

There are some software packages that help with generating CWL `CommandLineTool`s
for existing command line tools written in Python:

* [argparse2tool](https://github.com/erasche/argparse2tool#cwl-specific-functionality): Generate CWL CommandLineTool wrappers (and/or Galaxy tool descriptions) from Python programs that use argparse. Also supports the [click](http://click.pocoo.org) argument parser.
* [pypi2cwl](https://github.com/common-workflow-language/pypi2cwl): Automatically run argparse2cwl on any package in PyPi.
* [python-cwlgen](https://github.com/common-workflow-language/python-cwlgen): Generate CommandLineTool and DockerRequirement programmatically

## Listing available steps

Steps loaded into the `WorkflowGenerator` can be listed with:

```
print wf.list_steps()
```

## Running workflows

Workflows created with scriptcwl can be run with:
```
cwl-runner workflow.cwl <arguments>
```

Or

```
chmod +x workflow.cwl
./workflow.cwl <arguments>
```

## Scattering steps

Scriptcwl supports scattering steps. To scatter a step, keyword arguments
`scatter` and `scatter_method` must be provided when a step is added to the
workflow. To scatter a step called `echo`, which has a single input argument
`message`, this would look like:

```
output = wf.echo(message=input1, scatter='message', scatter_method='nested_crossproduct')
```

The type of `message`, should be an array (e.g., an array of strings).

To scatter over multiple variables, `scatter` also accepts a list of input names:

```
output = wf.echo(message1=input1, message2=input2, scatter=['message1', 'message2'], scatter_method='nested_crossproduct')
```
