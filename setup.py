# -*- coding: utf-8 -*-
"""Installer for the zopyx.typesense package."""

from setuptools import find_packages
from setuptools import setup


long_description = '\n\n'.join([
    open('README.rst').read(),
    open('CONTRIBUTORS.rst').read(),
    open('CHANGES.rst').read(),
])


setup(
    name='zopyx.typesense',
    version='1.0a1',
    description="Typesense integration with Plone 6",
    long_description=long_description,
    # Get more from https://pypi.org/classifiers/
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords='Python Plone CMS',
    author='Andreas Jung',
    author_email='info@zopyx.com',
    url='https://github.com/collective/zopyx.typesense',
    project_urls={
        'PyPI': 'https://pypi.python.org/pypi/zopyx.typesense',
        'Source': 'https://github.com/collective/zopyx.typesense',
        'Tracker': 'https://github.com/collective/zopyx.typesense/issues',
        # 'Documentation': 'https://zopyx.typesense.readthedocs.io/en/latest/',
    },
    license='GPL version 2',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['zopyx'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    python_requires="==2.7",
    install_requires=[
        'setuptools',
        # -*- Extra requirements: -*-
        'z3c.jbot',
        'Products.GenericSetup>=1.8.2',
        'plone.api>=1.8.4',
        'plone.restapi < 7.0.0a1',
        'plone.app.dexterity',
        'plone.app.referenceablebehavior',
        'plone.app.relationfield',
        'plone.app.lockingbehavior',
        'plone.schema',
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
