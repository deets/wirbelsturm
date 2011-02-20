import os
import sys
from setuptools import setup, find_packages

setup(
    name="WirbelSturm",
    version="0.1",
    description="Tornado Chat Integration Example",
    author="Diez B. Roggisch",
    author_email="deets@web.de",
    url="http://bitbucket.org/deets/wirbelsturm",
    license="MIT",
    packages=find_packages(exclude=['ez_setup', 'tests']),
    package_data = {'': ['*.html', '*.txt', '*.rst', '*.tpl']},
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        "abl.jquery",
        "abl.util",
        "bottle",
        "PasteDeploy",
        "PasteScript",
        "tornado",
        "tw.forms",
        "WSGIUtils",
        ],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Widget Sets',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    entry_points={
        'console_scripts': [
            'ws_frontend = wirbelsturm.frontend:main',
            ],
        'paste.app_factory': [
            'main=wirbelsturm.frontend:app_factory',
            ]
        },
)
