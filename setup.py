from setuptools import setup, find_packages
from linvam import __version__

setup(
    name='LinVAM',
    version=__version__,
    packages=find_packages(where='.'),
    url='https://github.com/stele95/LinVAM',
    license='GPL-3.0',
    author='stele',
    author_email='stefanstele95@hotmail.com',
    description='Linux Voice Activated Macros',
    install_requires=[
        'PyQt6',
        'srt',
        'requests',
        'tqdm',
        'sounddevice',
        'vosk'
    ],
    keywords='macros voice linvam linvamrun',
    entry_points={
        'console_scripts': [
            'linvam = linvam.main:start_linvam',
            'linvamrun = linvam.linvamrun:start_linvamrun'
        ]
    },
    classifiers=[
            'Environment :: Console',
            'Environment :: X11 Applications :: Qt',
            'Intended Audience :: Developers',
            'Intended Audience :: End Users/Desktop',
            'Intended Audience :: System Administrators',
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Operating System :: POSIX',
            'Programming Language :: Python :: 3.10',
            'Programming Language :: Python :: 3.11',
            'Programming Language :: Python :: 3.12'
            'Topic :: Games/Entertainment',
            'Topic :: Utilities'
        ]
)
