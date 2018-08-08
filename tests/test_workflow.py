from __future__ import print_function

import pytest
from shutil import copytree
from scriptcwl import WorkflowGenerator
from scriptcwl.library import load_yaml


def setup_workflowgenerator(tmpdir):
    toolsdir = tmpdir.join('tools').strpath
    workflows = tmpdir.join('workflows').strpath
    filenames = tmpdir.join('file-names').strpath
    misc = tmpdir.join('misc').strpath
    copytree('tests/data/tools', toolsdir)
    copytree('tests/data/workflows', workflows)
    copytree('tests/data/file-names', filenames)
    copytree('tests/data/misc', misc)
    wf = WorkflowGenerator()
    return wf


class TestWorkflowGenerator(object):
    def test_load(self):
        wf = WorkflowGenerator()
        wf.load('tests/data/tools')

        step_keys = wf.steps_library.steps.keys()
        step_keys = sorted(step_keys)
        assert step_keys == ['echo', 'multiple-out-args', 'wc']

    def test_load_with_list(self):
        wf = WorkflowGenerator()
        wf.load(step_list=['tests/data/workflows/echo-wc.cwl',
                           'tests/data/tools'])
        # 'https://raw.githubusercontent.com/WhatWorksWhenForWhom/nlppln/develop/cwl/anonymize.cwl',\
        step_keys = wf.steps_library.steps.keys()
        step_keys = sorted(step_keys)
        assert step_keys == ['echo', 'echo-wc', 'multiple-out-args', 'wc']

    def test_load_duplicate_cwl_step(self, tmpdir):
        wf = setup_workflowgenerator(tmpdir)
        wf.load(steps_dir=tmpdir.join('tools').strpath)
        with pytest.warns(UserWarning):
            wf.load(step_file=tmpdir.join('tools', 'echo.cwl').strpath)

    def test_save_with_tools(self, tmpdir):
        wf = setup_workflowgenerator(tmpdir)
        wf.load(steps_dir=tmpdir.join('tools').strpath)
        wf.set_documentation('Counts words of a message via echo and wc')

        wfmessage = wf.add_input(wfmessage='string')
        echoed = wf.echo(message=wfmessage)
        wced = wf.wc(file2count=echoed)
        wf.add_outputs(wfcount=wced)

        wf_filename = tmpdir.join('workflows/echo-wc.cwl').strpath
        wf.save(wf_filename, relative=True)

        # make workflows contents relative to tests/data/tools directory
        actual = load_yaml(wf_filename)
        expected_wf_filename = 'tests/data/workflows/echo-wc.cwl'
        expected = load_yaml(expected_wf_filename)

        print('  actual:', actual)
        print('expected:', expected)
        assert actual == expected

    def test_save_with_workflow(self, tmpdir):
        wf = setup_workflowgenerator(tmpdir)
        wf.load(tmpdir.join('workflows').strpath)

        wfmessage = wf.add_input(wfmessage='string')
        wced = wf.echo_wc(wfmessage=wfmessage)
        wf.add_outputs(wfcount=wced)

        wf_filename = tmpdir.join('echo-wc.cwl').strpath
        wf.save(wf_filename, relative=True)

        # make workflows contents relative to tests/data/tools directory
        actual = load_yaml(wf_filename)
        expected_wf_filename = 'tests/data/echo-wc.workflowstep.cwl'
        expected = load_yaml(expected_wf_filename)

        print('  actual:', actual)
        print('expected:', expected)
        assert actual == expected

    def test_save_with_scattered_step(self, tmpdir):
        wf = setup_workflowgenerator(tmpdir)
        wf.load(tmpdir.join('tools').strpath)

        msgs = wf.add_input(wfmessages='string[]')
        echoed = wf.echo(
            message=msgs,
            scatter='message',
            scatter_method='nested_crossproduct')
        wf.add_outputs(out_files=echoed)

        wf_filename = tmpdir.join('echo-scattered.cwl').strpath
        wf.save(wf_filename, relative=True)

        # make workflows contents relative to tests/data/tools directory
        actual = load_yaml(wf_filename)
        expected_wf_filename = 'tests/data/echo.scattered.cwl'
        expected = load_yaml(expected_wf_filename)

        print('  actual:', actual)
        print('expected:', expected)
        assert actual == expected

    def test_save_with_inline_tools(self, tmpdir):
        wf = WorkflowGenerator()
        wf.load('tests/data/tools')
        wf.set_documentation('Counts words of a message via echo and wc')

        wfmessage = wf.add_input(wfmessage='string')
        echoed = wf.echo(message=wfmessage)
        wced = wf.wc(file2count=echoed)
        wf.add_outputs(wfcount=wced)

        wf_filename = tmpdir.join('echo-wc.cwl').strpath
        wf.save(wf_filename, inline=True)

        # Strip absolute paths from ids
        actual = load_yaml(wf_filename)
        expected_wf_filename = 'tests/data/workflows/echo-wc_inline.cwl'
        expected = load_yaml(expected_wf_filename)

        # Random id's will differ and that's ok, so just remove them
        def remove_random_ids(step):
            del(step['outputs'][0]['outputBinding']['glob'])
            del(step['stdout'])

        remove_random_ids(actual['steps']['wc']['run'])
        remove_random_ids(actual['steps']['echo']['run'])
        remove_random_ids(expected['steps']['wc']['run'])
        remove_random_ids(expected['steps']['echo']['run'])

        print('  actual:', actual)
        print('expected:', expected)
        assert actual == expected

    def test_save_with_pack(self, tmpdir):
        wf = WorkflowGenerator()
        wf.load('tests/data/tools')
        wf.set_documentation('Counts words of a message via echo and wc')

        wfmessage = wf.add_input(wfmessage='string')
        echoed = wf.echo(message=wfmessage)
        wced = wf.wc(file2count=echoed)
        wf.add_outputs(wfcount=wced)

        wf_filename = tmpdir.join('echo-wc.cwl').strpath
        wf.save(wf_filename, pack=True)

        with WorkflowGenerator() as wf2:
            wf2.load(wf_filename)
            # wf_filename shouldn't be in the steps library, because it is a
            # packed workflow
            assert len(wf2.steps_library.steps.keys()) == 0

    def test_save_with_wd(self, tmpdir):
        wf = WorkflowGenerator(working_dir=tmpdir.join('wd').strpath)
        wf.load('tests/data/tools')

        wfmessage = wf.add_input(wfmessage='string')
        echoed = wf.echo(message=wfmessage)
        wced = wf.wc(file2count=echoed)
        wf.add_outputs(wfcount=wced)

        wf_filename = tmpdir.join('echo-wc.cwl').strpath
        wf.save(wf_filename, wd=True)

        actual = load_yaml(wf_filename)
        expected_wf_filename = 'tests/data/workflows/echo-wc_wd.cwl'
        expected = load_yaml(expected_wf_filename)

        print('  actual:', actual)
        print('expected:', expected)
        assert actual == expected

    def test_save_with_wd_no_wd(self, tmpdir):
        wf = WorkflowGenerator()

        assert wf.get_working_dir() is None

        wf.load('tests/data/tools')

        wfmessage = wf.add_input(wfmessage='string')
        echoed = wf.echo(message=wfmessage)
        wced = wf.wc(file2count=echoed)
        wf.add_outputs(wfcount=wced)

        wf_filename = tmpdir.join('echo-wc.cwl').strpath

        with pytest.raises(ValueError):
            wf.save(wf_filename, wd=True)

    def test_save_with_relative_url(self, tmpdir):
        wf = WorkflowGenerator()
        url = 'https://raw.githubusercontent.com/NLeSC/scriptcwl/master/' \
              'tests/data/tools/echo.cwl'
        wf.load(step_file=url)

        wfmessage = wf.add_input(wfmessage='string')
        echoed = wf.echo(message=wfmessage)
        wf.add_outputs(echoed=echoed)

        wf_filename = tmpdir.join('echo-wf.cwl').strpath
        wf.save(wf_filename, relative=True)

    def test_add_shebang_to_saved_cwl_file(self, tmpdir):
        wf = WorkflowGenerator()
        wf.load('tests/data/tools')

        wfmessage = wf.add_input(wfmessage='string')
        echoed = wf.echo(message=wfmessage)
        wced = wf.wc(file2count=echoed)
        wf.add_outputs(wfcount=wced)

        wf_filename = tmpdir.join('echo-wc.cwl').strpath
        wf.save(wf_filename, validate=False)

        with open(wf_filename) as f:
            shebang = f.readline()

        assert shebang == '#!/usr/bin/env cwl-runner\n'

    def test_detect_wrong_type(self):
        wf = WorkflowGenerator()
        wf.load('tests/data/tools')
        x = wf.add_input(msg='string')
        x = 3
        with pytest.raises(ValueError):
            wf.echo(message=x)


class TestWorkflowGeneratorWithScatteredStep(object):
    def test_scatter_method_incorrect(self):
        wf = WorkflowGenerator()
        wf.load('tests/data/tools')

        msgs = wf.add_input(wfmessages='string[]')

        with pytest.raises(ValueError):
            wf.echo(message=msgs, scatter='message', scatter_method='blah')

    def test_scatter_method_correct(self):
        scatter_methods = [
            'dotproduct', 'nested_crossproduct', 'flat_crossproduct'
        ]

        for method in scatter_methods:
            wf = WorkflowGenerator()
            wf.load('tests/data/tools')

            msgs = wf.add_input(wfmessages='string[]')

            echoed = wf.echo(
                message=msgs, scatter='message', scatter_method=method)
            assert echoed.step_name == 'echo'
            assert echoed.output_name == 'echoed'

    def test_scatter_variable_incorrect(self):
        wf = WorkflowGenerator()
        wf.load('tests/data/tools')

        msgs = wf.add_input(wfmessages='string[]')

        with pytest.raises(ValueError):
            wf.echo(
                message=msgs,
                scatter='incorrect',
                scatter_method='nested_crossproduct')

    def test_scatter_variable_correct(self):
        scatter_methods = [
            'dotproduct', 'nested_crossproduct', 'flat_crossproduct'
        ]

        for method in scatter_methods:
            wf = WorkflowGenerator()
            wf.load('tests/data/tools')

            msgs = wf.add_input(wfmessages='string[]')

            echoed = wf.echo(
                message=msgs, scatter='message', scatter_method=method)
            assert echoed.step_name == 'echo'
            assert echoed.output_name == 'echoed'

    def test_missing_scatter_argument(self):
        wf = WorkflowGenerator()
        wf.load('tests/data/tools')

        msgs = wf.add_input(wfmessages='string[]')

        with pytest.raises(ValueError):
            wf.echo(message=msgs, scatter_method='nested_crossproduct')

    def test_missing_scatter_method_argument(self):
        wf = WorkflowGenerator()
        wf.load('tests/data/tools')

        msgs = wf.add_input(wfmessages='string[]')

        with pytest.raises(ValueError):
            wf.echo(message=msgs, scatter='message')


class TestWorkflowGeneratorTypeChecking(object):
    def test_step_with_compatible_input(self):
        wf = WorkflowGenerator()
        wf.load('tests/data/tools')

        wfmessage = wf.add_input(wfmessage='string')
        echoed = wf.echo(message=wfmessage)

    def test_step_with_incompatible_input(self):
        wf = WorkflowGenerator()
        wf.load('tests/data/tools')

        wfmessage = wf.add_input(wfmessage='string')
        with pytest.raises(ValueError):
            wced = wf.wc(file2count=wfmessage)

    def test_step_with_scattered_input(self):
        wf = WorkflowGenerator()
        wf.load('tests/data/tools')

        msgs = wf.add_input(wfmessages='string[]')
        wf.echo(message=msgs, scatter='message', scatter_method='dotproduct')

    def test_step_with_compatible_step_output(self):
        wf = WorkflowGenerator()
        wf.load('tests/data/tools')

        wfmessage = wf.add_input(wfmessage='string')
        echoed = wf.echo(message=wfmessage)
        wced = wf.wc(file2count=echoed)

    def test_step_with_incompatible_step_output(self):
        wf = WorkflowGenerator()
        wf.load('tests/data/tools')

        infile = wf.add_input(infile='File')
        wced = wf.wc(file2count=infile)
        with pytest.raises(ValueError):
            echoed = wf.echo(message=wced)

    def test_step_with_scattered_step_output(self):
        wf = WorkflowGenerator()
        wf.load('tests/data/tools')

        msgs = wf.add_input(msgs='string[]')
        echoed = wf.echo(message=msgs, scatter='message',
                         scatter_method='dotproduct')
        wced = wf.wc(file2count=echoed, scatter='file2count',
                     scatter_method='dotproduct')

    def test_scattered_step_with_scalar_input(self):
        wf = WorkflowGenerator()
        wf.load('tests/data/tools')

        wfmessage = wf.add_input(message='string')
        with pytest.raises(ValueError):
            echoed = wf.echo(message=wfmessage, scatter='message',
                             scatter_method='dotproduct')

    def test_optional_type(self):
        wf = WorkflowGenerator()
        wf.load('tests/data/tools')

        # This could work, if you pass a string for input, even if
        # the echo step requires an input. So we expect it to work.
        wfmessage = wf.add_input(message='string?')
        echod = wf.echo(message=wfmessage)

    def test_required_to_optional(self):
        wf = WorkflowGenerator()
        wf.load('tests/data/tools')

        # out_dir is optional, attaching to non-optional input
        # should work.
        wf_infiles = wf.add_input(in_files='File[]')
        wf_outdir = wf.add_input(out_dir='string')
        wf_counselors = wf.add_input(counselors='string[]')
        out_files, meta_out = wf.multiple_out_args(
                in_files=wf_infiles, out_dir=wf_outdir,
                counselors=wf_counselors)

    def test_optional_to_optional_type(self):
        wf = WorkflowGenerator()
        wf.load('tests/data/tools')

        wf_infiles = wf.add_input(in_files='File[]')
        wf_outdir = wf.add_input(out_dir='string?')
        wf_counselors = wf.add_input(counselors='string[]')
        out_files, meta_out = wf.multiple_out_args(
                in_files=wf_infiles, out_dir=wf_outdir,
                counselors=wf_counselors)


class TestWorkflowGeneratorWithStepsAddedMultipleTimes(object):
    def test_generate_step_name(self):
        wf = WorkflowGenerator()
        wf.load('tests/data/tools')

        wfmessage = wf.add_input(wfmessage='string')

        name = wf._generate_step_name('echo')
        echoed = wf.echo(message=wfmessage)

        assert name == 'echo'
        assert name == echoed.step_name

        name = wf._generate_step_name('echo')
        echoed2 = wf.echo(message=wfmessage)

        assert name != 'echo'
        assert name == echoed2.step_name

    def test_validate_with_inline_tools(self):
        wf = WorkflowGenerator()
        wf.load('tests/data/tools')

        wfmessage = wf.add_input(wfmessage='string')
        echoed = wf.echo(message=wfmessage)
        echoed2 = wf.echo(message=wfmessage)
        wf.add_outputs(echoed2=echoed2)

        wf.validate(inline=True)


class TestWorkflowGeneratorWithDefaultValuesForInputParameters(object):
    def test_default_value_for_workflow_input(self):
        wf = WorkflowGenerator()

        wf.add_input(input1='string', default='test')
        obj = wf.to_obj()['inputs']['input1']
        assert obj['type'] == 'string'
        assert obj['default'] == 'test'

    def test_only_default_for_workflow_input(self):
        wf = WorkflowGenerator()

        with pytest.raises(ValueError):
            wf.add_input(default='test')

    def test_add_multiple_inputs_and_default(self):
        wf = WorkflowGenerator()

        with pytest.raises(ValueError):
            wf.add_input(input1='string', input2='string', default='test')


class TestWorkflowGeneratorWithLabelsForInputParameters(object):
    def test_label_for_workflow_input(self):
        wf = WorkflowGenerator()

        wf.add_input(input1='string', label='test label')
        obj = wf.to_obj()['inputs']['input1']
        assert obj['type'] == 'string'
        assert obj['label'] == 'test label'

    def test_only_label_for_workflow_input(self):
        wf = WorkflowGenerator()

        with pytest.raises(ValueError):
            wf.add_input(label='test')

    def test_only_label_and_default_for_workflow_input(self):
        wf = WorkflowGenerator()

        with pytest.raises(ValueError):
            wf.add_input(label='test', default='test')


class TestWorkflowGeneratorWithEnumAsInputParameter(object):
    def test_enum_as_workflow_input(self):
        wf = WorkflowGenerator()

        wf.add_input(input1='enum', symbols=['one', 'two', 'three'])
        obj = wf.to_obj()['inputs']['input1']
        assert obj['type']['type'] == 'enum'
        assert obj['type']['symbols'] == ['one', 'two', 'three']

    def test_no_symbols_for_enum_input(self):
        wf = WorkflowGenerator()

        with pytest.raises(ValueError):
            wf.add_input(input1='enum')

    def test_only_symbols_for_enum_input(self):
        wf = WorkflowGenerator()

        with pytest.raises(ValueError):
            wf.add_input(symbols=['one', 'two', 'three'])

    def test_empty_symbols_for_enum_input(self):
        wf = WorkflowGenerator()

        with pytest.raises(ValueError):
            wf.add_input(input1='enum', symbols=[])

    def test_symbols_is_a_list(self):
        wf = WorkflowGenerator()

        with pytest.raises(ValueError):
            wf.add_input(input1='enum', symbols='nolist')

    def test_convert_symbols_to_list_of_strings(self):
        wf = WorkflowGenerator()

        wf.add_input(input1='enum', symbols=[1, 2, 3])
        obj = wf.to_obj()['inputs']['input1']

        assert obj['type']['symbols'] == ['1', '2', '3']

    def test_combine_enum_with_label(self):
        wf = WorkflowGenerator()

        wf.add_input(input1='enum', symbols=['one', 'two', 'three'],
                     label='test label')
        obj = wf.to_obj()['inputs']['input1']
        assert obj['label'] == 'test label'


class TestWorkflowGeneratorAsContextManager(object):
    def test_use_workflow_generator_as_context_manager(self):
        with WorkflowGenerator() as wf:
            assert wf._wf_closed is False
        assert wf._wf_closed is True

    def test_error_on_using_closed_workflow_generator(self):
        with WorkflowGenerator() as wf:
            pass
        with pytest.raises(ValueError):
            wf._closed()


class TestNamingWorkflowInputs(object):
    def test_wf_inputs_with_the_same_name(self):
        with WorkflowGenerator() as wf:
            wf.add_input(msg='string')
            with pytest.raises(ValueError):
                wf.add_input(msg='string')

    def test_wf_inputs_with_the_same_name_default_value(self):
        with WorkflowGenerator() as wf:
            wf.add_input(msg='string', default='Hello World!')
            with pytest.raises(ValueError):
                wf.add_input(msg='string', default='Hello World!')


class TestWorkflowLabels(object):
    def test_set_label(self):
        with WorkflowGenerator() as wf:
            wf.set_label('test')

            obj = wf.to_obj()
            assert obj['label'] == 'test'


class TestWorkflowStepsWithSpecialFileNames(object):
    def test_add_step_with_underscores(self, tmpdir):
        wf = setup_workflowgenerator(tmpdir)
        step_file = tmpdir.join('file-names/echo_with_underscores.cwl').strpath
        wf.load(step_file=step_file)
        msg = wf.add_input(msg='string')
        wf.echo_with_underscores(message=msg)

    def test_add_step_with_minuses(self, tmpdir):
        wf = setup_workflowgenerator(tmpdir)
        step_file = tmpdir.join('file-names/echo-with-minuses.cwl').strpath
        wf.load(step_file=step_file)
        msg = wf.add_input(msg='string')
        wf.echo_with_minuses(message=msg)

    def test_add_step_with_minuses_and_underscores(self, tmpdir):
        wf = setup_workflowgenerator(tmpdir)
        sf = tmpdir.join('file-names/echo-with-minuses_and_underscores.cwl')
        step_file = sf.strpath
        wf.load(step_file=step_file)
        msg = wf.add_input(msg='string')
        wf.echo_with_minuses_and_underscores(message=msg)

    def test_load_step_with_duplicate_python_name(self, tmpdir):
        wf = setup_workflowgenerator(tmpdir)
        with pytest.warns(UserWarning):
            wf.load(steps_dir=tmpdir.join('file-names').strpath)


class TestWorkflowStepsListOfInputsFromWorkflowInputsOrStepOutputs(object):
    def test_add_step_with_list_of_inputs(self, tmpdir):
        wf = setup_workflowgenerator(tmpdir)
        step_file = tmpdir.join('misc/echo2.cwl').strpath
        wf.load(step_file=step_file)

        str1 = wf.add_input(str1='string')
        str2 = wf.add_input(str2='string')

        wf.echo2(message=[str1, str2])

    def test_add_step_with_list_of_inputs_unequal_types(self, tmpdir):
        wf = setup_workflowgenerator(tmpdir)
        step_file = tmpdir.join('misc/echo2.cwl').strpath
        wf.load(step_file=step_file)

        str1 = wf.add_input(str1='string')
        str2 = wf.add_input(str2='int')

        with pytest.raises(ValueError):
            wf.echo2(message=[str1, str2])

    def test_add_step_with_list_of_inputs_wrong_type(self, tmpdir):
        wf = setup_workflowgenerator(tmpdir)
        step_file = tmpdir.join('misc/echo2.cwl').strpath
        wf.load(step_file=step_file)

        str1 = wf.add_input(str1='int')
        str2 = wf.add_input(str2='int')

        with pytest.raises(ValueError):
            wf.echo2(message=[str1, str2])


class TestWorkflowWithNonPythonStepInputAndOutputNames(object):
    def test_add_step_with_non_python_input_and_output_names(self, tmpdir):
        wf = setup_workflowgenerator(tmpdir)

        step_file = tmpdir.join('misc/non-python-names.cwl').strpath
        wf.load(step_file=step_file)

        msg1 = wf.add_input(msg1='string')
        msg2 = wf.add_input(msg2='string?')

        echo_out = wf.non_python_names(first_message=msg1,
                                       optional_message=msg2)

        wf.add_outputs(out=echo_out)

    def test_type_checking_with_non_python_input_name(self, tmpdir):
        wf = setup_workflowgenerator(tmpdir)

        step_file = tmpdir.join('misc/non-python-names.cwl').strpath
        wf.load(step_file=step_file)

        msg1 = wf.add_input(msg1='int')
        msg2 = wf.add_input(msg2='string?')

        with pytest.raises(ValueError):
            wf.non_python_names(first_message=msg1,
                                optional_message=msg2)
