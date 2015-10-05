import os
import sys
from distutils.sysconfig import get_python_lib
from setuptools import setup, find_packages


# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

packages = find_packages('.')

# Dynamically calculate the version based on orchestra.VERSION.
version = __import__('orchestra').get_version()


setup(
    name = "django-orchestra",
    version = version,
    author = "Marc Aymerich",
    author_email = "marcay@pangea.org",
    url = "https://github.com/glic3rinu/django-orchestra",
    license = "GPLv3",
    description = "A framework for building web hosting control panels",
    long_description = (
        "There are a lot of widely used open source hosting control panels, "
        "however none of them seems apropiate when you already have a production "
        "service infrastructure or simply you want a particular architecture.\n"
        "The goal of this project is to provide the tools for easily build a fully "
        "featured control panel that fits any service architecture."),
    include_package_data = True,
    scripts=[
        'orchestra/bin/orchestra-admin',
        'orchestra/bin/orchestra-beat',
    ],
    packages = packages,
    classifiers = [
        'Development Status :: 1 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Server/Management',
    ]
)
