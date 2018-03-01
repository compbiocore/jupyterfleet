from setuptools import setup

setup(
	name='jupyterfleet',
	version='0.1',
	url='https://github.com/compbiocore/jupyterfleet',
	licence='https://raw.githubusercontent.com/compbiocore/jupyterfleet/master/LICENSE',
	scripts=['jupyterfleet.py', 'generate_directory.sh'],
	install_requires=['awscli']
)