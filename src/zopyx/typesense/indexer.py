import pprint
import furl
import plone.api
import typesense
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zope.component import queryMultiAdapter
from zopyx.typesense.interfaces import ITypesenseSettings
from zopyx.typesense import LOG

from .browser.views import View

def remove_content(context, event):

    client = View(event.object, event.object.REQUEST).get_typesense_client()
    if not client:
        return

    enabled = plone.api.portal.get_registry_record("enabled", ITypesenseSettings)
    if not enabled:
        LOG.info("Typesense indexing disabled")
        return

    obj = event.object
    site_id = plone.api.portal.get().getId()

    id = f"{site_id}-{obj.UID()}"
    collection = plone.api.portal.get_registry_record("collection", ITypesenseSettings)
    response = client.collections[collection].documents[id].delete()
    LOG.info(f"Deleted {id}")

def update_content(context, event):

    client = View(event.object, event.object.REQUEST).get_typesense_client()
    if not client:
        return

    enabled = plone.api.portal.get_registry_record("enabled", ITypesenseSettings)
    if not enabled:
        LOG.info("Typesense indexing disabled")
        return

    obj = event.object

    try:
        review_state = plone.api.content.get_state(obj)
    except:
        review_state = ''

    site_id = plone.api.portal.get().getId()

    d = dict()
    d['id'] = f"{site_id}-{obj.UID()}"
    d['id_original'] = obj.getId()
    d['title'] = obj.Title()
    d['description'] = obj.Description()
    d['language'] = obj.Language()
    d['portal_type'] = obj.portal_type
    d['text'] = "xxxxx"
    d['review_state'] = review_state
    d['path'] = '/'.join(obj.getPhysicalPath())
    d['created'] = obj.created().ISO8601()
    d['modified'] = obj.modified().ISO8601()
    d['effective'] = obj.effective().ISO8601()
    d['expires'] = obj.expires().ISO8601()
    d['subject'] = obj.Subject()
    d['uid'] = obj.UID()
#    pprint.pprint(d)

    collection = plone.api.portal.get_registry_record("collection", ITypesenseSettings)

    response = client.collections[collection].documents.upsert(d)
    LOG.info(f"Upsert {d['id']}")
