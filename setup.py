from setuptools import setup, find_packages

install_requires = [
    'Cython',  # this is somewhat ignored... must be installed before this package itself
    'pyliblo',
]

extras_require= {
    'ipython': ['IPython'],
    'evdev': ['evdev'],
    'eviocgname': ['ioctl_opt'],
}

extras_require['all'] = [dep for deps in extras_require.values() for dep in deps]


setup(
    name='WacOsc',
    version='0.0.1',
    description='Wacom to Open Sound Control.',
    author='castix',
    author_email='castix@autistici.org',
    packages=find_packages(),
    install_requires=install_requires,
    extras_require=extras_require,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    zip_safe=False,
)
