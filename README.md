# scriptcwl

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/8f383bca18384d8187c10c27affa9d53)](https://www.codacy.com/app/j-vanderzwaan/scriptcwl?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=NLeSC/scriptcwl&amp;utm_campaign=Badge_Grade)
[![Codacy Badge](https://api.codacy.com/project/badge/Coverage/8f383bca18384d8187c10c27affa9d53)](https://www.codacy.com/app/j-vanderzwaan/scriptcwl?utm_source=github.com&utm_medium=referral&utm_content=NLeSC/scriptcwl&utm_campaign=Badge_Coverage)
[![Build Status](https://travis-ci.org/NLeSC/scriptcwl.svg?branch=master)](https://travis-ci.org/NLeSC/scriptcwl)
[![Documentation Status](https://readthedocs.org/projects/scriptcwl/badge/?version=latest)](http://scriptcwl.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/scriptcwl.svg)](https://badge.fury.io/py/scriptcwl)
[![PyPI](https://img.shields.io/pypi/pyversions/scriptcwl.svg)](https://pypi.python.org/pypi/scriptcwl)


scriptcwl is a Python package to create workflows in
[common workflow language](http://www.commonwl.org/). If you give it a set of CWL
`CommandLineTool`s, you can create a workflow by writing a Python script. This can
be done interactively using [Jupyter Notebooks](http://jupyter.org/).

## Example

As a first example we can make a Hello World workflow. We use a commanlinetool (`hello.cwl`) which runs the echo command and looks like this in CWL:
```
#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: CommandLineTool
baseCommand: echo
inputs:
  message:
    type: string
    inputBinding:
      position: 1
outputs: []
```

It takes a variable `message` and runs the echo command. To run the commandlinetool one needs to specify the message input variable using a yml file (`echo-job.yml`):

```
message: Hello world!
message2: Hello again!
```

You can incorporate the `hello.cwl` commandlinetool from above in a workflow using scriptcwl in this way:
```python
from scriptcwl import WorkflowGenerator

wf = WorkflowGenerator()
wf.load(step_file="hello.cwl")

print(wf.list_steps())

message = wf.add_inputs(message="string")
message2 = wf.add_inputs(message2="string")

hello = wf.hello(message=message)
hello2 = wf.hello(message=message2)

print(wf.list_steps())

wf.save('python_cwl_test.cwl')
```

You load the `WorkflowGenerator` and make an instance of it. You can load commandlinetools and workflows using `wf.load()`. The loaded cwl files can be shown using `wf.list_steps()`. Inputs of the workflow can be made using `wf.add_inputs()`. In the example above we add two inputs named `message` and `message2` which are of the type string. Next we create a step in the workflow named `hello` and `hallo2` using `wf.hello(message=message)`. The input of the step (`message`) is linked to the workflow input `message` and `message2` created before. The created workflow is saved to a cwl file using `wf.save()`. Now you can run the workflow with `cwl-runner python_cwl_test.cwl echo-job.cwl`.

A more usefull example using nlppln is to generate the [anonymize pipeline](https://github.com/WhatWorksWhenForWhom/nlppln/blob/develop/cwl/anonymize.cwl), which [replaces named entities with their type](https://github.com/WhatWorksWhenForWhom/nlppln#anonymize), (from the
[nlppln](https://github.com/WhatWorksWhenForWhom/nlppln) package), you'd have to write:

```python
from scriptcwl import WorkflowGenerator

with WorkflowGenerator() as wf:
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

  frogout = wf.frog_dir(in_files=txt_dir)
  saf = wf.frog_to_saf(in_files=frogout)
  ner_stats = wf.save_ner_data(in_files=saf)
  new_saf = wf.replace_ner(metadata=ner_stats, in_files=saf)
  txt = wf.saf_to_txt(in_files=new_saf)

  wf.add_outputs(ner_stats=ner_stats, txt=txt)

  wf.save('anonymize.cwl')
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
python setup.py develop test
```

## Useful tools

There are some software packages that help with generating CWL `CommandLineTool`s
for existing command line tools written in Python:

* [argparse2tool](https://github.com/erasche/argparse2tool#cwl-specific-functionality): Generate CWL CommandLineTool wrappers (and/or Galaxy tool descriptions) from Python programs that use argparse. Also supports the [click](http://click.pocoo.org) argument parser.
* [pypi2cwl](https://github.com/common-workflow-language/pypi2cwl): Automatically run argparse2cwl on any package in PyPi.
* [python-cwlgen](https://github.com/common-workflow-language/python-cwlgen): Generate CommandLineTool and DockerRequirement programmatically
