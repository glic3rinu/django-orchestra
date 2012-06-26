#!/usr/bin/env python

import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages
import os, os.path
import sys

DIRNAME = os.path.dirname(__file__)
APPDIR = os.path.join(DIRNAME, 'orchestra/apps')
if not APPDIR in sys.path:
    sys.path.insert(0,APPDIR)

# Dynamically calculate the version based on django.VERSION.
#version = __import__('satchmo_store').__version__
packages = find_packages('orchestra/apps')
packages.append('media')
#packages.append('docs')
packages.append('orchestra_skeleton')

setup(name = "Orchestra",
      version = "1",
      author = "Marc Aymerich",
      author_email = "marcay@pangea.org",
      url = "http://orchestra.calmisko.org",
      license = "GPLv3",
      description = "Web hosting control panel.",
      long_description = "Orchestra is a fully featured web hosting control panel based on django reusable applications.",
      include_package_data = True,
      zip_safe = False,
      package_dir = {
      '' : 'orchestra/apps',
      'media' : 'orchestra/media',
#      'docs' : 'docs',
      'orchestra_skeleton' : 'orchestra/projects/skeleton',
      },
#      scripts=['scripts/clonesatchmo.py'],
#      setup_requires=["setuptools_hg"],
      packages = packages,
      classifiers = [
      'Development Status :: 1 - Alpha',
      'License :: OSI Approved :: GPL v3 License',
      'Operating System :: OS Independent', 
      'Topic :: Server/Management',
      ]
)

