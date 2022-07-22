from setuptools import setup, find_packages
from packageinfo import NAME, VERSION
import subprocess

import clean_install

#CFD environment installation
subprocess.call("osp/wrappers/simcfd/modules/foam_install")

# Read description
with open('README.md', 'r') as readme:
    README_TEXT = readme.read()

# main setup configuration class
setup(
    name=NAME,
    version=VERSION,
    author='Giorgio La Civita, DIN, Università di Bologna',
    description='The wrapper of NanoFOAM (NanoDOME + CFD + Elenbaas) for SimPhoNy',
    keywords='simphony, cuds, NanoDOME, CFD, Elenbaas',
    long_description=README_TEXT,
    install_requires=[
        'osp-core>=3.0.0',
        'numpy',
        'scipy',
        'psutil',
        'matplotlib'
    ],
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8.0",
    entry_points={
        'wrappers': [
            'cfdsession = osp.wrappers.simcfd:CFDSession',
            'nanosession = osp.wrappers.simnanodome:NanoDOMESession',
            'elenbaassession = osp.wrappers.simelenbaas:ElenbaasSession',
            'coupledreactorsession = osp.wrappers.simcoupledreactor:CoupledReactorSession',
		]
	}
)
