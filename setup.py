from setuptools import setup, find_namespace_packages

with open('README.rst', 'r') as fh:
    long_description = fh.read()

setup(
    name='redcap-booster',
    version='0.0.1',
    author='Phil Schumm',
    author_email='pschumm@uchicago.edu',
    description='API for providing external services to REDCap',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://gitlab.com/pschumm/redcap-booster',
    packages=find_namespace_packages(where='.'),
    install_requires=['fastapi == 0.66.0',
                      'uvicorn[standard] == 0.17.6',
                      'gunicorn == 20.1.0',
                      'click == 8.0.1',
                      'pluginbase == 1.0.1',
                      'python-dotenv == 0.18.0',
                      'requests == 2.26.0'],
    entry_points = {
        'console_scripts':['rbutils=redcap_booster.cli:cli']
    }
)
