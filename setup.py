#!/usr/bin/env python

from setuptools import setup

setup(
    name = "blinky",
    version = "0.1",
    description = "Blinky the Blink camera dashboard.",
    author = "Matt Kubilus",
    packages=['blinky'],
    package_dir={'blinky': 'src'},
    #scripts=['src/blinky'],
    entry_points = {
        'console_scripts': ['blinky=blinky.blinky:main'],
    },
    #package_dir={'.': 'static','templates':'templates'},
    package_data={
        'blinky': [
            'static/css/*.css',
            'static/videos/.keep',
            'templates/*.html'
        ]
    },
    install_requires=[
        'pywebview',
        'blinkpy == 0.14.01',
        'Flask >= 0.12'
    ],
    python_requires='>=3'

)
