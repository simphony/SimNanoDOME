from setuptools import setup, find_packages
from packageinfo import NAME, VERSION

# Read description
with open('README.md', 'r') as readme:
    README_TEXT = readme.read()

# main setup configuration class
setup(
    name=NAME,
    version=VERSION,
    author='Giorgio La Civita, DIN, University of Bologna',
    description='The NanoFOAM Wrapper (NanoDOME + CFD + Elenbaas) for SimPhoNy',
    keywords='simphony, cuds, NanoDOME, CFD, Elenbaas',
    long_description=README_TEXT,
    install_requires=[
        'osp-core>=3.0.0',
        'numpy',
        'scipy',
        'psutil',
        'matplotlib'
    ],
    tests_require=[
        'numpy',
    ],
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.9.0",
    entry_points={
        'wrappers': [
            'cfdsession = osp.wrappers.simcfd:CFDSession',
            'nanosession = osp.wrappers.simnanodome:NanoDOMESession',
            'elenbaassession = osp.wrappers.simelenbaas:ElenbaasSession',
            'coupledreactorsession = osp.wrappers.simcoupledreactor:CoupledReactorSession',
		]
	}
)
