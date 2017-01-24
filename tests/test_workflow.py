import os
import yaml

from scriptcwl import WorkflowGenerator


def load_yaml(filename, remove):
    with open(filename) as myfile:
        return yaml.safe_load(myfile.read().replace(remove, ''))


class TestWorkflowGenerator(object):
    def test_load(self):
        wf = WorkflowGenerator()
        wf.load('tests/data/tools')

        step_keys = wf.steps_library.keys()
        step_keys.sort()
        assert step_keys == ['echo', 'wc']

    def test_save_with_tools(self, tmpdir):
        wf = WorkflowGenerator()
        wf.load('tests/data/tools')
        wf.set_documentation('Counts words of a message via echo and wc')

        wfmessage = wf.add_inputs(wfmessage='string')
        echoed = wf.echo(message=wfmessage)
        wced = wf.wc(file2count=echoed)
        wf.add_outputs(wfcount=wced)

        wf_filename = tmpdir.join('echo-wc.cwl').strpath
        wf.save(wf_filename)

        # make workflows contents relative to tests/data/tools directory
        actual = load_yaml(wf_filename, os.getcwd() + '/tests/data/tools')
        expected_wf_filename = 'tests/data/workflows/echo-wc.cwl'
        expected = load_yaml(expected_wf_filename, '../tools')

        assert actual == expected

    def test_save_with_workflow(self, tmpdir):
        wf = WorkflowGenerator()
        wf.load('tests/data/workflows')

        wfmessage = wf.add_inputs(wfmessage='string')
        wced = wf.echo_wc(wfmessage=wfmessage)
        wf.add_outputs(wfcount=wced)

        wf_filename = tmpdir.join('echo-wc.cwl').strpath
        wf.save(wf_filename)

        # make workflows contents relative to tests/data/tools directory
        actual = load_yaml(wf_filename, os.getcwd() + '/tests/data/workflows')
        expected_wf_filename = 'tests/data/echo-wc.workflowstep.cwl'
        expected = load_yaml(expected_wf_filename, '../workflows')

        assert actual == expected

    def test_add_shebang_to_saved_cwl_file(self, tmpdir):
        wf = WorkflowGenerator()
        wf.load('tests/data/tools')

        wfmessage = wf.add_inputs(wfmessage='string')
        echoed = wf.echo(message=wfmessage)
        wced = wf.wc(file2count=echoed)
        wf.add_outputs(wfcount=wced)

        wf_filename = tmpdir.join('echo-wc.cwl').strpath
        wf.save(wf_filename)

        with open(wf_filename) as f:
            shebang = f.readline()

        assert shebang == '#!/usr/bin/env cwl-runner\n'