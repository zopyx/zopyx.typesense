# -*- coding: utf-8 -*-
"""Installer for the zopyx.typesense package."""

from setuptools import find_packages
from setuptools import setup


long_description = '\n\n'.join([
    open('README.md').read(),
])


setup(
    name='zopyx.typesense',
    version='1.0.0a7',
    description="Typesense integration with Plone 6",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # Get more from https://pypi.org/classifiers/
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 5.2",
        "Framework :: Plone :: 6.0",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords='Python Plone CMS search fulltext indexing factedsearch Typesense',
    author='Andreas Jung',
    author_email='info@zopyx.com',
    url='https://github.com/zopyx/zopyx.typesense',
    project_urls={
        'PyPI': 'https://pypi.python.org/pypi/zopyx.typesense',
        'Source': 'https://github.com/zopyx/zopyx.typesense',
        'Tracker': 'https://github.com/zopyx/zopyx.typesense/issues',
        # 'Documentation': 'https://zopyx.typesense.readthedocs.io/en/latest/',
    },
    license='GPL version 2',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['zopyx'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        # -*- Extra requirements: -*-
        'z3c.jbot',
        'typesense',
        'furl',
        'zopyx.plone.persistentlogger',
        'zopyx.ipsumplone',
        'html-text',
        'huey',
        'tika',
        'typer',
        'furl',
        'progressbar2',
    ],
    extras_require={
        'test': [
            'plone.app.testing',
            # Plone KGS does not use this version, because it would break
            # Remove if your package shall be part of coredev.
            # plone_coredev tests as of 2016-04-01.
            'plone.testing>=5.0.0',
            'plone.app.robotframework[debug]',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    [console_scripts]
    update_locale = zopyx.typesense.locales.update:update_locale
    """,
)
