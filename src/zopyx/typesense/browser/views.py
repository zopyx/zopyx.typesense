from Products.Five.browser import BrowserView

import json
import typesense
import plone.api
import pprint
import time

import furl
from zope.interface.interfaces import ComponentLookupError
from zope.lifecycleevent import ObjectModifiedEvent
from zope.event import notify

from zopyx.typesense.interfaces import ITypesenseSettings
from zopyx.typesense import LOG
from zopyx.typesense import _

class View(BrowserView):


    def get_typesense_client(self):
        try:
            api_key = plone.api.portal.get_registry_record("api_key", ITypesenseSettings)
            node1_url = plone.api.portal.get_registry_record("node1_url", ITypesenseSettings)
            node2_url = plone.api.portal.get_registry_record("node2_url", ITypesenseSettings)
            node3_url = plone.api.portal.get_registry_record("node3_url", ITypesenseSettings)
        except (KeyError, ComponentLookupError):
            return None

        nodes = list()
        for url in (node1_url, node2_url, node3_url):
            if not url:
                continue

            f = furl.furl(url)
            nodes.append(dict(
                    host=f.host,
                    port=f.port,
                    protocol=f.scheme
                    ))


        client = typesense.Client({
            'api_key': api_key,
            'nodes': nodes,
            'connection_timeout_seconds': 10
        })
        return client

    def recreate_collection(self):

        client = self.get_typesense_client()
        if not client:
            return

        collection = plone.api.portal.get_registry_record("collection", ITypesenseSettings)

        all_collections = [collection["name"] for collection in client.collections.retrieve()]

        if collection in all_collections:
            try:
                client.collections[collection].delete()
                LOG.info(f"Deleted Typesense collection {collection}")
            except Exception as e:
                LOG.exception(f"Could not delete Typesense collection {collection}")
                raise


        create_response = client.collections.create({
            "name": "typesense",
            "fields": [
                {"name": "path", "type": "string"},
                {"name": "id", "type": "string"},
                {"name": "title", "type": "string"},
                {"name": "description", "type": "string"},
                {"name": "text", "type": "string"},
                {"name": "language", "type": "string", "facet": True},
                {"name": "portal_type", "type": "string", "facet": True},
                {"name": "review_state", "type": "string", "facet": False},
                {"name": "subject", "type": "string[]", "facet": False},
                {"name": "created", "type": "string", "facet": False},
                {"name": "modified", "type": "string", "facet": False},
                {"name": "effective", "type": "string", "facet": False},
                {"name": "expires", "type": "string", "facet": False},
                {"name": "document_type_order", "type": "int32"},
            ],
            "default_sorting_field": "document_type_order",
            "attributesToSnippet": [
                'title',
                'description',
               'text:20',
                ],
            "attributesToHighlight": [
                'title',
                'description',
               'text:20',
                ]
        })
        LOG.info(f"Created Typesense collection {collection}")

        self.request.response.setStatus(201)

    def indexed_content(self):
        """ Return indexed content for current context object """

        site_id = plone.api.portal.get().getId()
        obj_id = f"{site_id}-{self.context.UID()}"

        client = self.get_typesense_client()
        collection = plone.api.portal.get_registry_record("collection", ITypesenseSettings)

        try:
            document = client.collections[collection].documents[obj_id].retrieve()
        except typesense.exceptions.ObjectNotFound:
            document = {}

        return document

    def export_documents(self):
        """ Export all documents from current collection as JSONLines """

        client = self.get_typesense_client()
        collection = plone.api.portal.get_registry_record("collection", ITypesenseSettings)

        self.request.response.setHeader("content-type", "application/json")
        self.request.response.setHeader("content-disposition", f"attachment; filename={collection}.jsonl")
        return client.collections[collection].documents.export()

    def collection_information(self):
        """ Retrieve Collection information """

        client = self.get_typesense_client()
        collection = plone.api.portal.get_registry_record("collection", ITypesenseSettings)

        info =  client.collections[collection].retrieve()
        return pprint.pformat(info, indent=4)

    def reindex_all(self):
        """ Reindex all """

        ts = time.time()

        client = self.get_typesense_client()
        collection = plone.api.portal.get_registry_record("collection", ITypesenseSettings)

        self.recreate_collection()

        catalog = plone.api.portal.get_tool("portal_catalog")
        brains = catalog()
        num_brains = len(list(brains))
        for i, brain in enumerate(brains):
            if i % 1000 == 0:
                LOG.info(f"{i + 1}/{num_brains} objects indexed")
            obj = brain.getObject()
            obj.reindexObject()
            event = ObjectModifiedEvent(obj)
            notify(event)

        duration = time.time() - ts
        LOG.info(f"All content reindexed ({i} items), duration {duration:.2f} seconds")

        portal = plone.api.portal.get()
        plone.api.portal.show_message(_("All content reindexed"), request=self.request)
        self.request.response.redirect(portal.absolute_url() + "/@@typesense-admin")

