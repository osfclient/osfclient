# Always prefer setuptools over distutils
from setuptools import setup, find_packages


setup(
    name='osfclient',
    # update `osfclient/__init__.py` as well
    version='0.0.3',

    description='An OSF command-line library',
    long_description='An OSF command-line client and library.',

    # The project's main homepage.
    url='https://github.com/dib-lab/osf-cli',

    # Author details
    author='The OSF-cli authors',
    # Choose your license
    license='BSD3',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'License :: OSI Approved :: BSD License',
        'Topic :: Utilities'
    ],

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(),

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['requests', 'tqdm', 'six'],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'osf=osfclient.__main__:main',
        ],
    },
)
