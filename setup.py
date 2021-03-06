from setuptools import setup

setup(
    name='Contractual',
    version='0.1.3',
    packages=['contractual'],
    license='MIT',
    # metadata for upload to PyPI
    author="The Narrativ Company, Inc.",
    author_email="admin@narrativ.com",
    description="Enforce contract tests based on yml data files",
    keywords="testing contract tests",
    test_suite='tests/test_contractual.py',
    tests_require=['pyyaml'],
)
