# scriptcwl

scriptcwl is a Python package to generate and edit workflows in
[common workflow language](http://www.commonwl.org/). The idea is to create
cwl workflows by writing a Python script, which can be done interactively using
[Jupyter Notebooks](http://jupyter.org/).

For example, to generate the [anonymize pipeline](https://github.com/WhatWorksWhenForWhom/nlppln/blob/develop/cwl/workflows/anonymize.cwl) (from the
[nlppln](https://github.com/WhatWorksWhenForWhom/nlppln) package), you'd have to write:

```
import scriptcwl
from scriptcwl import WorkflowGenerator, load_steps

steps = load_steps('/path/to/cwl/steps/')

wf = WorkflowGenerator()
wf.load(steps)

txt_dir = wf.add_inputs(txt_dir='Directory')
frogout = wf.frog_dir(dir_in=txt_dir)
saf = wf.frog_to_saf(in_files=frogout)
ner_stats = wf.save_ner_data(in_files=saf)
new_saf = wf.replace_ner(metadata=ner_stats, in_files=saf)
txt = wf.saf_to_txt(in_files=new_saf)
wf.add_output(ner_stats=ner_stats, txt=txt)

wf.save('anonymize.cwl')
```

## Installation

```
git clone git@github.com:NLeSC/scriptcwl.git
cd scriptcwl
git checkout develop
python setup.py develop
```
