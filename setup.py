from setuptools import setup, find_packages
import os

setup(
    name='try2connect',
    version='0.1',
    packages=find_packages(),
    author='Nikolay Denisov',
    license='© Carbonsoft',
    author_email='moddingshell@gmail.com',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.md')).read(),
    scripts=[os.path.join('utils/', script) for script in os.listdir('utils/')],
    install_requires=[
        'requests',
        'gevent',
        'dnspython',
    ]
)
