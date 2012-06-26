from setuptools import setup, find_packages

VERSION = '0.0.1'

LONG_DESCRIPTION = open('README.rst').read()

setup(name='dployment-center',
    version=VERSION,
    description="dploy's build server",
    long_description=LONG_DESCRIPTION,
    keywords='',
    author='Reuven V. Gonzales',
    author_email='reuven@tobetter.us',
    url="https://github.com/ravenac95/dployment-center",
    license='MIT',
    platforms='*nix',
    packages=find_packages(exclude=['ez_setup', 'examples', 'prototyping', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'pyzmq',
    ],
    entry_points={
        'console_scripts': [
            'dployment-center = dploymentcenter.main:main',
        ],
    },
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Operating System :: POSIX',
        'Topic :: Software Development :: Build Tools',
    ],
)
