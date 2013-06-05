from setuptools import setup, find_packages
import os

version = '1.0'

long_description = open('README.txt').read()

setup(name='zenoss.europadev',
      version=version,
      description="",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='',
      author_email='',
      url='https://github.com/zenoss/europa-dev',
      license='private',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zenoss'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      [console_scripts]
      git-zen = zenoss.europadev.git:main
      """,
      )
