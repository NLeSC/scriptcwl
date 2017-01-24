from scriptcwl.yamlmultiline import is_multiline


def test_is_multiline():
    assert not is_multiline('single line string')
    assert is_multiline('multi\nline\nstring')
