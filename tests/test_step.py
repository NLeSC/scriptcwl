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

    def test_is_workflow(self, step):
        assert not step.is_workflow

    def test_get_input_names(self, step):
        names = step.get_input_names()
        assert len(names) == 1
        firstname = names[0]
        assert firstname.endswith('message')


class TestWithWorkflow(object):
    @pytest.fixture
    def step(self):
        return Step('tests/data/workflows/echo-wc.cwl')

    def test_is_workflow(self, step):
        assert step.is_workflow

    def test_get_input_names(self, step):
        names = step.get_input_names()
        assert len(names) == 1
        firstname = names[0]
        assert firstname.endswith('wfmessage')


class TestInputOptional(object):
    @pytest.fixture
    def step(self):
        return Step('tests/data/tools/echo.cwl')

    def test_argument_is_optional(self, step):
        assert step._input_optional({'type': 'string?'})
        assert step._input_optional({'type': [u'null', 'string']})
        assert step._input_optional({'type': 'string', 'default': 'test'})

    def test_argument_is_not_optional(self, step):
        assert not step._input_optional({'type': 'string'})


class TestMultipleOutputArgs(object):
    @pytest.fixture
    def step(self):
        return Step('tests/data/tools/multiple-out-args.cwl')

    def test_has_multiple_out_args(self, step):
        assert len(step.to_obj()['out']) == 2


class TestStepNameInWorkflow(object):
    @pytest.fixture
    def step(self):
        return Step('tests/data/tools/echo.cwl')

    def test_no_name_in_workflow(self, step):
        with pytest.raises(AttributeError):
            step.name_in_workflow == 'echo'

    def test_set_name_in_workflow(self, step):
        step._set_name_in_workflow('echo')
        assert step.name_in_workflow == 'echo'


class TestRemoveShebangForInlineSteps(object):
    def test_inline_step_without_shebang(self):
        step = Step('tests/data/echo-no-shebang.cwl')
        step.to_obj(inline=True)


class TestPrintStep(object):

    def test_str_(self):
        step = Step('tests/data/tools/echo.cwl')
        assert str(step) == 'echoed = wf.echo(message)'

    def test_str_non_python_names(self):
        step = Step('tests/data/misc/non-python-names.cwl')
        o = 'echo_out = wf.non_python_names(first_message[, optional_message])'
        assert str(step) == o
