from __future__ import print_function

import os
import sys

import pytest
from ruamel import yaml

from scriptcwl import WorkflowGenerator


def load_yaml(filename, remove):
    with open(filename) as myfile:
        return yaml.safe_load(myfile.read().replace(remove, ''))


class TestWorkflowGenerator(object):
    def test_load(self):
        wf = WorkflowGenerator()
        wf.load('tests/data/tools')

        step_keys = wf.steps_library.keys()
        step_keys = sorted(step_keys)
        assert step_keys == ['echo', 'multiple-out-args', 'wc']

    def test_load_with_list(self):
        wf = WorkflowGenerator()
        wf.load(step_list=['tests/data/workflows/echo-wc.cwl',\
            'tests/data/tools'])
        #'https://raw.githubusercontent.com/WhatWorksWhenForWhom/nlppln/develop/cwl/anonymize.cwl',\
        step_keys = wf.steps_library.keys()
        step_keys = sorted(step_keys)
        assert step_keys == ['echo', 'echo-wc', 'multiple-out-args', 'wc']

    def test_save_with_tools(self, tmpdir):
        wf = WorkflowGenerator()
        wf.load(os.path.join('tests','data','tools'))
        wf.set_documentation('Counts words of a message via echo and wc')

        wfmessage = wf.add_input(wfmessage='string')
        echoed = wf.echo(message=wfmessage)
        wced = wf.wc(file2count=echoed)
        wf.add_outputs(wfcount=wced)

        wf_filename = tmpdir.join('echo-wc.cwl').strpath
        wf.save(wf_filename)

        # make workflows contents relative to tests/data/tools directory
        if "win" in sys.platform:
            to_remove =  os.path.join(os.getcwd(), os.path.join('tests','data','tools'))+"\\"
        else:
            to_remove =  os.path.join(os.getcwd(), os.path.join('tests','data','tools'))+"/"
        actual = load_yaml(wf_filename,to_remove)
        expected_wf_filename = os.path.join('tests','data','workflows','echo-wc.cwl')
        expected = load_yaml(expected_wf_filename, "../tools/")

        print('  actual:', actual)
        print('expected:', expected)
        assert actual == expected

    def test_save_with_workflow(self, tmpdir):
        wf = WorkflowGenerator()
        wf.load(os.path.join('tests','data','workflows'))

        wfmessage = wf.add_input(wfmessage='string')
        wced = wf.echo_wc(wfmessage=wfmessage)
        wf.add_outputs(wfcount=wced)

        wf_filename = tmpdir.join('echo-wc.cwl').strpath
        wf.save(wf_filename)

        # make workflows contents relative to tests/data/tools directory
        if "win" in sys.platform:
            to_remove =  os.path.join(os.getcwd(), os.path.join('tests','data','workflows'))+"\\"
        else:
            to_remove =  os.path.join(os.getcwd(), os.path.join('tests','data','workflows'))+"/"
        actual = load_yaml(wf_filename, to_remove)
        expected_wf_filename = os.path.join('tests','data','echo-wc.workflowstep.cwl')
        expected = load_yaml(expected_wf_filename, '../workflows/')

        print('  actual:', actual)
        print('expected:', expected)
        assert actual == expected

    def test_save_with_scattered_step(self, tmpdir):
        wf = WorkflowGenerator()
        wf.load(os.path.join('tests','data','tools'))

        msgs = wf.add_input(wfmessages='string[]')
        echoed = wf.echo(
            message=msgs,
            scatter='message',
            scatter_method='nested_crossproduct')
        wf.add_outputs(out_files=echoed)

        wf_filename = tmpdir.join('echo-scattered.cwl').strpath
        wf.save(wf_filename)

        # make workflows contents relative to tests/data/tools directory
        if "win" in sys.platform:
            to_remove =  os.path.join(os.getcwd(), os.path.join('tests','data','tools'))+"\\"
        else:
            to_remove =  os.path.join(os.getcwd(), os.path.join('tests','data','tools'))+"/"
        actual = load_yaml(wf_filename, to_remove)
        expected_wf_filename = os.path.join('tests','data','echo.scattered.cwl')
        expected = load_yaml(expected_wf_filename, '../tools/')

        print('  actual:', actual)
        print('expected:', expected)
        assert actual == expected

    def test_add_shebang_to_saved_cwl_file(self, tmpdir):
        wf = WorkflowGenerator()
        wf.load('tests/data/tools')

        wfmessage = wf.add_input(wfmessage='string')
        echoed = wf.echo(message=wfmessage)
        wced = wf.wc(file2count=echoed)
        wf.add_outputs(wfcount=wced)

        wf_filename = tmpdir.join('echo-wc.cwl').strpath
        wf.save(wf_filename)

        with open(wf_filename) as f:
            shebang = f.readline()

        assert shebang == '#!/usr/bin/env cwltool\n'

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
            assert echoed == 'echo/echoed'

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
            assert echoed == 'echo/echoed'

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


class TestWorkflowGeneratorWithStepsAddedMultipleTimes(object):
    def test_generate_step_name(self):
        wf = WorkflowGenerator()
        wf.load('tests/data/tools')

        wfmessage = wf.add_input(wfmessage='string')

        name = wf._generate_step_name('echo')
        echoed = wf.echo(message=wfmessage)

        assert name == 'echo'
        assert name == echoed.split('/')[0]

        name = wf._generate_step_name('echo')
        echoed2 = wf.echo(message=wfmessage)

        assert name != 'echo'
        assert name == echoed2.split('/')[0]


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
