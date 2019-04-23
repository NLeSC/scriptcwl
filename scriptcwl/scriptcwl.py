import sys
import os
import logging

from contextlib import contextmanager

logger = logging.getLogger(__name__)

legacy_cwltool = False


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
    from cwltool.load_tool import fetch_document

    try:
        from cwltool.load_tool import resolve_and_validate_document
    except ImportError:
        from cwltool.load_tool import validate_document

        legacy_cwltool = True


def load_cwl(fname):
    """Load and validate CWL file using cwltool
    """
    logger.debug('Loading CWL file "{}"'.format(fname))
    # Fetching, preprocessing and validating cwl

    # Older versions of cwltool
    if legacy_cwltool:
        try:
            (document_loader, workflowobj, uri) = fetch_document(fname)
            (document_loader, _, processobj, metadata, uri) = \
                validate_document(document_loader, workflowobj, uri)
        except TypeError:
            from cwltool.context import LoadingContext, getdefault
            from cwltool import workflow
            from cwltool.resolver import tool_resolver
            from cwltool.load_tool import resolve_tool_uri

            loadingContext = LoadingContext()
            loadingContext.construct_tool_object = getdefault(
                loadingContext.construct_tool_object,
                workflow.default_make_tool)
            loadingContext.resolver = getdefault(loadingContext.resolver,
                                                 tool_resolver)

            uri, tool_file_uri = resolve_tool_uri(
                fname, resolver=loadingContext.resolver,
                fetcher_constructor=loadingContext.fetcher_constructor)

            document_loader, workflowobj, uri = fetch_document(
                    uri, resolver=loadingContext.resolver,
                    fetcher_constructor=loadingContext.fetcher_constructor)
            document_loader, avsc_names, processobj, metadata, uri = \
                validate_document(
                    document_loader, workflowobj, uri,
                    loadingContext.overrides_list, {},
                    enable_dev=loadingContext.enable_dev,
                    strict=loadingContext.strict,
                    preprocess_only=False,
                    fetcher_constructor=loadingContext.fetcher_constructor,
                    skip_schemas=False,
                    do_validate=loadingContext.do_validate)
    # Recent versions of cwltool
    else:
        (loading_context, workflowobj, uri) = fetch_document(fname)
        loading_context, uri = resolve_and_validate_document(loading_context,
                                                             workflowobj, uri)
        document_loader = loading_context.loader
        processobj = workflowobj
        metadata = loading_context.metadata

    return document_loader, processobj, metadata, uri


def is_url(path):
    return path.startswith('http://') or path.startswith('https://')
