from .api import API
from .browser.views import View
from plone.app.textfield import RichText
from plone.dexterity.utils import iterSchemata
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zope.component import queryMultiAdapter
from zope.interface.interfaces import ComponentLookupError
from zope.schema import getFields
from zopyx.typesense import LOG
from zopyx.typesense.interfaces import ITypesenseSettings

import furl
import html2text
import plone.api
import pprint
import time
import typesense
import zope.schema


def can_index():
    try:
        api.portal.get_registry_record("collection", ITypesenseSettings)
        return True
    except:
        return False


def remove_content(context, event):
    """Async removal of content"""

    if not can_index():
        return

    ts = time.time()
    ts_api = API()
    ts_api.unindex_document(context)
    duration = (time.time() - ts) * 1000
    LOG.info(f"Unindexing {context.getId(), context.absolute_url(1)}, {duration} ms")


def update_content(context, event):
    """Async indexing of content"""

    if not can_index():
        return

    ts = time.time()
    ts_api = API()
    ts_api.index_document(context)
    duration = (time.time() - ts) * 1000
    LOG.info(f"Indexing {context.getId(), context.absolute_url(1)}, {duration} ms")
