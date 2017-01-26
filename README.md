# scriptcwl

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/8f383bca18384d8187c10c27affa9d53)](https://www.codacy.com/app/j-vanderzwaan/scriptcwl?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=NLeSC/scriptcwl&amp;utm_campaign=Badge_Grade)
[![Codacy Badge](https://api.codacy.com/project/badge/Coverage/8f383bca18384d8187c10c27affa9d53)](https://www.codacy.com/app/j-vanderzwaan/scriptcwl?utm_source=github.com&utm_medium=referral&utm_content=NLeSC/scriptcwl&utm_campaign=Badge_Coverage)
[![Build Status](https://travis-ci.org/NLeSC/scriptcwl.svg?branch=master)](https://travis-ci.org/NLeSC/scriptcwl)
[![PyPI version](https://badge.fury.io/py/scriptcwl.svg)](https://badge.fury.io/py/scriptcwl)


scriptcwl is a Python package to generate and edit workflows in
[common workflow language](http://www.commonwl.org/). The idea is to create
cwl workflows by writing a Python script, which can be done interactively using
[Jupyter Notebooks](http://jupyter.org/).

For example, to generate the [anonymize pipeline](https://github.com/WhatWorksWhenForWhom/nlppln/blob/develop/cwl/anonymize.cwl) (from the
[nlppln](https://github.com/WhatWorksWhenForWhom/nlppln) package), you'd have to write:

```
import scriptcwl
from scriptcwl import WorkflowGenerator

wf = WorkflowGenerator()
wf.load('/path/to/dir/with/cwl/steps/')

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

## Running workflows

Workflows created with scriptcwl can be run with:
```
cwl-runnner workflow.cwl <arguments>
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
