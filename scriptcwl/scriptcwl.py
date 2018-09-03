import sys
import os
import pkg_resources

from contextlib import contextmanager


# Helper function to make the import of cwltool.load_tool quiet
@contextmanager
def quiet():
    # save stdout/stderr
    # Jupyter doesn't support setting it back to
    # sys.__stdout__ and sys.__stderr__
    _sys_stdout = sys.stdout
    _sys_stderr = sys.stderr
    # Divert stdout and stderr to devnull
    sys.stdout = sys.stderr = open(os.devnull, "w")
    try:
        yield
    finally:
        # Revert back to standard stdout/stderr
        sys.stdout = _sys_stdout
        sys.stderr = _sys_stderr


with quiet():
    # all is quiet in this scope
    from cwltool.load_tool import fetch_document, validate_document
    from cwltool.process import use_custom_schema
    import cwltool


def load_cwl(fname, enable_ext=False):
    """Load and validate CWL file using cwltool
    """
    # Fetching, preprocessing and validating cwl
    if enable_ext:
        print('Name in enable_ext', cwltool.main.__name__)
        res = pkg_resources.resource_stream(cwltool.main.__name__,
                                            'extensions.yml')
        use_custom_schema("v1.0", "http://commonwl.org/cwltool", res.read())
        res.close()

    (document_loader, workflowobj, uri) = fetch_document(fname)
    (document_loader, _, processobj, metadata, uri) = \
        validate_document(document_loader, workflowobj, uri)

    return document_loader, processobj, metadata, uri


def is_url(path):
    return path.startswith('http://') or path.startswith('https://')
