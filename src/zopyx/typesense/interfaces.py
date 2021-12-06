# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope.interface import Interface
from zope import schema
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from zopyx.typesense import _


class IBrowserLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""

class ITypesenseSettings(Interface):
    """ Connector settings """

    enabled = schema.Bool(title=_('Typesense integration enabled'),
                                    default=True)

    collection = schema.TextLine(title=_('Name of Typesense collection'),
                                    default='typesense',
                                    required=True)

    api_key = schema.TextLine(title=_('Typesense API key'),
                                    default='',
                                    required=False)

    node1_url = schema.TextLine(title=_('URL of Typesense node 1'),
                                         description=_('URL node 1'),
                                         default="http://localhost:8108",
                                         required=True)

    node2_url = schema.TextLine(title=_('URL of Typesense node 2'),
                                         description=_('URL node 2'),
                                         required=False)

    node3_url = schema.TextLine(title=_('URL of Typesense node 3'),
                                         description=_('URL node 3'),
                                         required=False)
