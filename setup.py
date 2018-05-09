
from setuptools import setup, find_packages


setup(
    name='extendy',
    version='0.1.0',
    description='A small framework for enabling extensions/plugins/addons in'
    ' your application.',
    long_description=open('README.rst', 'r').read(),
    keywords='extendy extension plugin addon framework',
    author='Jason Simeone',
    author_email='jay@classless.net',
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    url='https://github.com/jayclassless/extendy',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    zip_safe=True,
    include_package_data=True,
    install_requires=[
        'six',
    ],
)

