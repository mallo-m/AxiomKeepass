#!/usr/bin/python3

from setuptools import setup

setup(
    name='axiom-keepass',
    version='0.1.0',
    description='Remotely poison keepass installations and loot secrets',
    url='http://localhost',
    author='mallo',
    author_email='none',
    license='BSD 2-clause',
    packages=[
        'axiom_keepass',
        'axiom_keepass.core',
        'axiom_keepass.client'
    ],
    package_data={'': [
        '../Binaries/System.Windows.Forms.dll',
        '../Assembly/AxiomKeepass.cs',
        '../Assembly/AssemblyInfo.cs',
        '../Scripts/decrypt.sh',
        '../Scripts/sch_task.xml'
    ]},
    install_requires=[
        'argparse',
        'impacket',
        'friendlywords'
    ],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    entry_points={
        'console_scripts': ['axiom-keepass=axiom_keepass.__main__:main'],
    }
)

