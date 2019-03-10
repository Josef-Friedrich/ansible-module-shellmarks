from setuptools import setup
from os import path
import versioneer

# read the contents of your README file
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), 'rb') as f:
    long_description = f.read().decode("UTF-8")

setup(
    name='shellmarks',
    description='shellmarks is a ansible module to set bookmarks to commonly '
    'used directories like the tools shellmarks and bashmarks do.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author='Josef Friedrich',
    author_email='josef@friedrich.rocks',
    license='GPL3',
    url='https://github.com/Josef-Friedrich/ansible-module-shellmarks',
    install_requires=[
        'ansible',
        # test/utils/tox/requirements.txt
        'nose',
        'mock >= 1.0.1, < 1.1',
        'passlib',
        'coverage',
        'coveralls',
        'unittest2',
        'redis',
        'python-memcached',
        'python-systemd',
        'pycrypto',
        'botocore',
        'boto3',
        'pytest',
        'flake8'
    ],
)
