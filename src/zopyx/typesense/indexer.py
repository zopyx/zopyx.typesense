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
    pprint.pprint(d)

    collection = plone.api.portal.get_registry_record("collection", ITypesenseSettings)

    response = client.collections[collection].documents.create(d)
    print(response)
