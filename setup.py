"""Tool to generate CWL workflows"""
# Always prefer setuptools over distutils
from os import path

from setuptools import find_packages, setup


def read(fname):
    """Define read function to read README.md in long description."""
    return open(path.join(path.dirname(__file__), fname)).read()


setup(
    name='scriptcwl',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.8.1',

    description=__doc__,
    long_description=read('README.rst'),
    # The project's main homepage.
    url='https://github.com/nlesc/scriptcwl',

    download_url='https://github.com/NLeSC/scriptcwl/archive/0.8.0.tar.gz',

    # Author details
    author='Janneke van der Zwaan',
    author_email='j.vanderzwaan@esciencecenter.nl',

    # Choose your license
    license='Apache 2.0',

    include_package_data=True,

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: Apache Software License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'

    ],

    # What does your project relate to?
    keywords='cwl, workflow, pipeline, common workflow language',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(),

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
        'six',
        'cwltool>=1.0.20170727112954',
        'click'],
    setup_requires=[
        # dependency for `python setup.py test`
        'pytest-runner',
        # dependencies for `python setup.py build_sphinx`
        'sphinx',
        'recommonmark'
    ],
    tests_require=[
        'pytest',
        'pytest-cov',
        'pycodestyle',
        'codacy-coverage',
        'pytest-datafiles',
    ],
)
