import os

from setuptools import setup


def read(file_name):
    """
    Read the contents of a text file and return its content.

    :param str file_name: The name of the file to read.

    :return: The content of the text file.
    :rtype: str
    """
    return open(
        os.path.join(os.path.dirname(__file__), file_name),
        encoding='utf-8'
    ).read()


setup(
    name='shellmarks',
    description='shellmarks is a ansible module to set bookmarks to commonly '
    'used directories like the tools shellmarks and bashmarks do.',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    version='0.0.0',
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
