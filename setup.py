from setuptools import setup

setup(
    name='redcap-booster',
    version='0.0.1',
    url='https://rcg.bsd.uchicago.edu/gitlab/rcg/redcap-booster.git',
    author='Research Computing Group',
    description='API for providing external services to REDCap',
    entry_points = {
        'console_scripts':['rbutils=redcap_booster.cli:cli'],
    },
    install_requires=['fastapi == 0.66.0',
                      'uvicorn[standard] == 0.14.0',
                      'gunicorn == 20.1.0',
                      'click == 8.0.1',
                      'pluginbase == 1.0.1',
                      'python-dotenv == 0.18.0']
)
