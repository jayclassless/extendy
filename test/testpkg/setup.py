
from setuptools import setup, find_packages


setup(
    name='extendy_testpkg',
    version='0.0.0',
    description='A package to facilitate the testing of extendy.',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=[
        #'extendy',
    ],
    entry_points={
        'extendytest': [
            'foo = extendy_testpkg:ThirdFooImplementation',
            'bar = extendy_testpkg:BarImplementation',
            'broken = extendy_testpkg:DoesntExist',
        ],
    },
)

