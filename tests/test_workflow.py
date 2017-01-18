from scriptcwl import WorkflowGenerator


class TestWorkflowGenerator(object):
    def test_load(self):
        wf = WorkflowGenerator()
        wf.load('tests/data/tools')

        step_keys = wf.steps_library.keys()
        step_keys.sort()
        assert step_keys == ['echo', 'wc']

    def test_save(self, tmpdir):
        wf = WorkflowGenerator()
        wf.load('tests/data/tools')
        wf.set_documentation('Counts words of a message via echo and wc')

        wfmessage = wf.add_inputs(wfmessage='string')

        echoed = wf.echo(message=wfmessage)
        wced = wf.wc(file2count=echoed)
        wf.add_outputs(wfcount=wced)

        wf_filename = tmpdir.join('echo-wc.cwl').strpath
        wf.save(wf_filename)

        expected_wf_filename = 'tests/data/workflows/echo-wc.cwl'

        with open(wf_filename) as f_actual:
            with open(expected_wf_filename) as f_expected:
                # TODO make paths in actual and expected the same
                assert f_actual.read() == f_expected.read()
