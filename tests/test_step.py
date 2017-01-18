import pytest

from schema_salad.validate import ValidationException

from scriptcwl.step import Step


def test_filenotfound():
    with pytest.raises(ValidationException):
        Step('tests/data/tools/idontexist.cwl')


class TestWithCommandLineTool(object):
    @pytest.fixture
    def step(self):
        return Step('tests/data/tools/echo.cwl')

    def test_get_input_names(self, step):
        names = step.get_input_names()
        assert len(names) == 1
        assert names[0].endswith('echo.cwl#message')


class TestWithWorkflow(object):
    @pytest.fixture
    def step(self):
        return Step('tests/data/workflows/echo-wc.cwl')

    def test_get_input_names(self, step):
        names = step.get_input_names()
        assert len(names) == 1
        assert names[0].endswith('echo-wc.cwl#wfmessage')
