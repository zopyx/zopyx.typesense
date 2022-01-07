import pprint
import furl
import plone.api
import typesense
import html2text
import time
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zope.component import queryMultiAdapter
from zopyx.typesense.interfaces import ITypesenseSettings
from plone.app.textfield import RichText
import zope.schema
from zopyx.typesense import LOG

from plone.dexterity.utils import iterSchemata
from zope.schema import getFields

from .browser.views import View

from .huey_tasks import ts_index
from .huey_tasks import ts_unindex

#
h2t = html2text.HTML2Text()
#


def remove_content(context, event):

    ts = time.time()

    client = View(event.object, event.object.REQUEST).get_typesense_client()
    if not client:
        return

    enabled = plone.api.portal.get_registry_record(
        'enabled', ITypesenseSettings
    )
    if not enabled:
        LOG.info('Typesense indexing disabled')
        return

    site_id = plone.api.portal.get().getId()
    id = f'{site_id}-{context.UID()}'

    collection = plone.api.portal.get_registry_record(
        'collection', ITypesenseSettings
    )
    document_path = '/'.join(context.getPhysicalPath())
    ts_unindex(client, collection, document_id=id, document_path=document_path)

    duration = (time.time() - ts) * 1000
    LOG.info(f'Unindexing {id, context.absolute_url(1)}, {duration} ms')


def update_content(context, event):

    ts = time.time()

    client = View(context, context.REQUEST).get_typesense_client()
    if not client:
        return

    enabled = plone.api.portal.get_registry_record(
        'enabled', ITypesenseSettings
    )
    if not enabled:
        LOG.info('Typesense indexing disabled')
        return

    try:
        review_state = plone.api.content.get_state(context)
    except:
        review_state = ''

    site_id = plone.api.portal.get().getId()

    obj = context

    d = dict()
    d['id'] = f'{site_id}-{obj.UID()}'
    d['id_original'] = obj.getId()
    d['title'] = obj.Title()
    d['description'] = obj.Description()
    d['language'] = obj.Language()
    d['portal_type'] = obj.portal_type
    d['review_state'] = review_state
    d['path'] = '/'.join(obj.getPhysicalPath())
    d['created'] = obj.created().ISO8601()
    d['modified'] = obj.modified().ISO8601()
    d['effective'] = obj.effective().ISO8601()
    d['expires'] = obj.expires().ISO8601()
    d['subject'] = obj.Subject()
    d['uid'] = obj.UID()
    d['document_type_order'] = 0

    # indexable text content
    indexable_text = []

    fields = {}
    schemes = iterSchemata(context)
    for schema in schemes:
        fields.update(getFields(schema))

    for name, field in fields.items():
        if isinstance(field, RichText):
            text = getattr(obj, name)
            if text and text.output:
                indexable_text.append(h2t.handle(text.output))
        elif isinstance(field, (zope.schema.Text, zope.schema.TextLine)):
            text = getattr(obj, name)
            indexable_text.append(text)

    indexable_text = [text for text in indexable_text if text]
    indexable_text = ' '.join(indexable_text)
    d['text'] = indexable_text

    collection = plone.api.portal.get_registry_record(
        'collection', ITypesenseSettings
    )
    ts_index(
        client, collection, d, document_id=d['id'], document_path=d['path']
    )

    duration = (time.time() - ts) * 1000

    LOG.info(f"Indexing {d['id'], d['path']}, {duration} ms")
