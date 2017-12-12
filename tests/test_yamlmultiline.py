from scriptcwl.yamlmultiline import is_multiline
from scriptcwl import WorkflowGenerator

import os


def test_is_multiline():
    assert not is_multiline('single line string')
    assert is_multiline('multi\nline\nstring')


def test_multiline_output(tmpdir):
    wf = WorkflowGenerator(working_dir=tmpdir.join('working_dir').strpath)
    wf.set_documentation('Testing a multiline\ndocumentation string')
    tmpfile = os.path.join(str(tmpdir), 'test.cwl')
    wf.save(tmpfile)
    with open(tmpfile) as f:
        contents = f.readlines()
        assert len(contents) > 7
