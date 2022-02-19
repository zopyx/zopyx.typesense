# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from .config import COLLECTION_SCHEMA_JSON, DEFAULT_REVIEW_STATES_TO_INDEX
from zope import schema
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zopyx.typesense import _


class IBrowserLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class ITypesenseSettings(Interface):
    """Connector settings"""

    enabled = schema.Bool(
        title=_("Typesense integration enabled"),
        default=True,
    )

    collection = schema.TextLine(
        title=_("Name of Typesense collection"),
        default="typesense",
        required=True,
    )

    api_key = schema.TextLine(
        title=_("Typesense Admin API key"),
        default="",
        required=True,
    )

    search_api_key = schema.TextLine(
        title=_("Typesense search API key"),
        default="",
        required=True,
    )

    node1_url = schema.TextLine(
        title=_("URL of Typesense node 1"),
        description=_("URL node 1"),
        default="http://localhost:8108",
        required=True,
    )

    node2_url = schema.TextLine(
        title=_("URL of Typesense node 2"),
        description=_("URL node 2"),
        required=False,
    )

    node3_url = schema.TextLine(
        title=_("URL of Typesense node 3"),
        description=_("URL node 3"),
        required=False,
    )

    tika_url = schema.TextLine(
        title=_("URL of Tika server for indexing office formats"),
        description=_("URL Tika server"),
        required=False,
    )

    review_states_to_index = schema.Text(
        title=_("Review states to index "),
        default=DEFAULT_REVIEW_STATES_TO_INDEX,
        required=True,
    )

    collection_schema = schema.Text(
        title=_("Collection schema"),
        default=COLLECTION_SCHEMA_JSON,
        required=True,
    )

    use_searchabletext = schema.Bool(
        title=_("Use SearchableText for indexing as default"),
        default=False,
    )


class ITypesenseIndexDataProvider(Interface):
    """Adapter for custom indexing"""

    def get_indexable_content(indexable_content):
        """This method get the default data dict with
        indexed_content (see api.py). The custom
        indexer method can modify or provide additional
        data to be indexed.

        Returns an updated dict of indexed_content
        """
