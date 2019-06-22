#!/usr/bin/env python

from distutils.core import setup

setup(
    name = "blinky",
    version = "0.1",
    description = "Blinky the Blink camera dashboard.",
    author = "Matt Kubilus",
    packages=['blinky'],
    scripts=['src/blinky.py'],
    #package_dir={'.': 'static','templates':'templates'},
    package_dir={'blinky': 'src'},
    package_data={
        'blinky': [
            'static/css/*.css',
            'static/videos/.keep',
            'templates/*.html'
        ]
    },
    python_requires='>=3'

)
