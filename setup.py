from setuptools import setup

setup(
    name='Contractual',
    version='0.1',
    packages=['contractual'],
    license='MIT',
    long_description=open('README.md').read(),
    # metadata for upload to PyPI
    author="Paul Becotte",
    author_email="pjbecotte@gmail.com",
    description="Enforce contract tests based on yml data files",
    keywords="testing contract tests",
    test_suite='tests/test_contractual.py',
    tests_require=['pyyaml'],
)