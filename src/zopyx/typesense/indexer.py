import pprint
import furl
import plone.api
import typesense
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zope.component import queryMultiAdapter
from zopyx.typesense.interfaces import ITypesenseSettings

from .browser.views import View

def index_content(context, event):

    client = View(event.object, event.object.REQUEST).get_typesense_client()
    if not client:
        return

    enabled = plone.api.portal.get_registry_record("collection", ITypesenseSettings)
    if not enabled:
        return

    try:
        review_state = plone.api.content.get_state(context)
    except:
        review_state = ''

    d = dict()
    d['id'] = context.getId()
    d['title'] = context.Title()
    d['description'] = context.Description()
    d['language'] = context.Language()
    d['portal_type'] = context.portal_type
    d['text'] = "xxxxx"
    d['review_state'] = review_state
    d['path'] = '/'.join(context.getPhysicalPath())
    d['created'] = context.created().ISO8601()
    d['modified'] = context.modified().ISO8601()
    d['effective'] = context.effective().ISO8601()
    d['expires'] = context.expires().ISO8601()
    d['subject'] = context.Subject()
    pprint.pprint(d)

    collection = plone.api.portal.get_registry_record("collection", ITypesenseSettings)

    response = client.collections[collection].documents.upsert(d)
    print(response)
