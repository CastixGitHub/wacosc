from setuptools import setup, find_packages

install_requires = [
    'Cython',  # this is somewhat ignored... must be installed before this package itself
    'pyliblo',
    'evdev',
    'IPython',
]

setup(
    name='WacOsc',
    version='0.0.1',
    description='Wacom to Open Sound Control.',
    author='castix',
    author_email='castix@autistici.org',
    packages=find_packages(),
    install_requires=install_requires,
        classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    zip_safe=False,
)
