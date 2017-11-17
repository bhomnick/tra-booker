#!/usr/bin/env python

from setuptools import setup, find_packages


CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Multimedia :: Graphics',
    'Topic :: Scientific/Engineering :: Image Recognition',
    'Topic :: Security',
]


setup(
    author="Ben Homnick",
    author_email="bhomnick@gmail.com",
    name="tra-captcha",
    version='0.0.1',
    description=("Captcha decoder for the Taiwan Railways Administration (TRA)"
                 " online ticketing system"),
    long_description=open('README.md').read(),
    license='MIT License',
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    packages=find_packages(exclude=['tests', 'scripts']),
    include_package_data=True,
    install_requires=[
        'numpy>=1.13.3',
        'Pillow>=4.3.0',
        'scipy>=1.0.0'
    ],
)
