#!/usr/bin/python3

from setuptools import setup
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
	name='eng_bot',
	version='0.1',
	description='Instagram engagement bot',
	author='Ruslan Yakushev',
	author_email='yakushev.rusl101@gmail.com',
	url='https://github.com/lrusifikator/engagement_bot',
	scripts=['bin/eng_bot'],
	packages=['eng_bot'],
	install_requires=requirements,
)