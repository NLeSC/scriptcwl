import pytest

import os
from pathlib import Path

from scriptcwl.library import load_yaml, load_steps


data_dir = Path(os.path.dirname(os.path.realpath(__file__))) / 'data' / 'misc'


@pytest.mark.datafiles(Path(data_dir) / 'align-dir-pack.cwl')
def test_load_yaml_packed(datafiles):
    cwl_file = datafiles.listdir()[0]

    assert {} == load_yaml(cwl_file)


@pytest.mark.datafiles(Path(data_dir) / 'align-dir-pack.cwl')
def test_load_steps_file_packed(datafiles):
    cwl_file = datafiles.listdir()[0]

    assert {} == load_steps(step_file=cwl_file)
