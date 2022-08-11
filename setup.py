# -*- mode: python ; coding: utf-8 -*-
from setuptools import setup
from setuptools.dist import check_entry_points

with open('README.md', encoding='utf-8') as readme:
    long_description = readme.read()

setup(name='marzin.org',
      version = '1.0',
      description = 'Markdown CMS',
      long_description = long_description,
      long_description_content_type = 'text/markdown',
      author = 'Antoine Marzin',
      license = 'MIT',
      url = 'https://marzin.org',
      packages = ['mdcms'],
      check_entry_points = {'console_scripts': ['mdcms = mdcms.mdcms:flaskapp']},
      keywords = 'lightweight cms markdown flask json webapp web',
      python_require = '>=3.7',
      install_requires = ['gunicorn', 'flask', 'markdown']
    )