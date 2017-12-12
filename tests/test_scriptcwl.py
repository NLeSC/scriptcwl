from scriptcwl.scriptcwl import is_url


def test_is_url():
    assert is_url('https://www.esciencecenter.nl/')
    assert is_url('http://www.esciencecenter.nl/')
    assert not is_url('file:///home/xxx/cwl-working-dir/test/cwl')
