from Products.Five.browser import BrowserView

import typesense
import plone.api

import furl
from zope.interface.interfaces import ComponentLookupError

from zopyx.typesense.interfaces import ITypesenseSettings

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

        try:
            client.collections[collection].delete()
            print(f"Deleted Typesense collection {collection}")
        except Exception as e:
            print(f"Could not delete Typesense collection {collection}")


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
            ],
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
        print(f"Created Typesense collection {collection}")
        print(create_response)

        self.request.response.setStatus(201)
