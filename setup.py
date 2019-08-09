# """
# The build/compilations setup
#
# >> python setup.py install
# """
import pip
import logging
import pkg_resources
try: from setuptools import setup
except ImportError: from distutils.core import setup
install_reqs = []

setup(
  name='su',
  version='0.1',
  author='David S. Hayden',
  author_email='dshayden@mit.edu',
  license='MIT',
  description='Slurm utility library',
  packages=["su"],
  scripts=['scripts/MakeSlurmJobFiles'],
  python_requires='>=3.6',
  classifiers=[
    "Development Status :: 5 - Production/Stable",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Intended Audience :: Information Technology",
    "Intended Audience :: Education",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
    "Topic :: Scientific/Engineering :: Image Recognition",
    "Topic :: Scientific/Engineering :: Visualization",
    "Topic :: Scientific/Engineering :: Image Segmentation",
    'Programming Language :: Python :: 3.6',
  ],
  keywords="slurm SLURM batch jobs",
)
