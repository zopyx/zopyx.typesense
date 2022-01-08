from .api import API
from .browser.views import View
from plone.app.textfield import RichText
from plone.dexterity.utils import iterSchemata
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zope.component import queryMultiAdapter
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


def remove_content(context, event):

    ts = time.time()
    ts_api = API()
    ts_api.unindex_document(context)
    duration = (time.time() - ts) * 1000
    LOG.info(f'Unindexing {context.getId(), context.absolute_url(1)}, {duration} ms')


def update_content(context, event):

    ts = time.time()
    ts_api = API()
    ts_api.index_document(context)
    duration = (time.time() - ts) * 1000
    LOG.info(f"Indexing {context.getId(), context.absolute_url(1)}, {duration} ms")
