from .huey_tasks import ts_index, ts_unindex
from plone import api
from plone.app.textfield import RichText
from plone.dexterity.utils import iterSchemata
from zope.event import notify
from zope.interface.interfaces import ComponentLookupError
from zope.lifecycleevent import ObjectModifiedEvent
from zope.schema import getFields
from zopyx.typesense import _, LOG
from zopyx.typesense.interfaces import ITypesenseSettings

import furl
import json
import pprint
import time
import typesense
import html2text
import zope.schema

h2t = html2text.HTML2Text()

COLLECTION_SCHEMA = {
    'name': None,
    'fields': [
        {'name': 'path', 'type': 'string'},
        {'name': 'id', 'type': 'string'},
        {'name': 'title', 'type': 'string'},
        {'name': 'description', 'type': 'string'},
        {'name': 'text', 'type': 'string'},
        {'name': 'language', 'type': 'string', 'facet': True},
        {'name': 'portal_type', 'type': 'string', 'facet': True},
        {'name': 'review_state', 'type': 'string', 'facet': False},
        {'name': 'subject', 'type': 'string[]', 'facet': False},
        {'name': 'created', 'type': 'string', 'facet': False},
        {'name': 'modified', 'type': 'string', 'facet': False},
        {'name': 'effective', 'type': 'string', 'facet': False},
        {'name': 'expires', 'type': 'string', 'facet': False},
        {'name': 'document_type_order', 'type': 'int32'},
    ],
    'default_sorting_field': 'document_type_order',
    'attributesToSnippet': [
        'title',
        'description',
        'text:20',
    ],
    'attributesToHighlight': [
        'title',
        'description',
        'text:20',
    ],
}


class API:
    @property
    def collection(self):
        """Return collection name from registry"""
        collection = api.portal.get_registry_record(
            'collection', ITypesenseSettings
        )
        return collection

    def index_document(self, obj):
        """Index document `obj`"""

        ts_index(
            ts_client=self.get_typesense_client(),
            collection=self.collection,
            data=self.indexable_content(obj),
            document_id=self.document_id(obj),
            document_path=self.document_path(obj),
        )

    def unindex_document(self, obj):
        """Unindex document `obj`"""

        ts_unindex(
            ts_client=self.get_typesense_client(),
            collection=self.collection,
            document_id=self.document_id(obj),
            document_path=self.document_path(obj),
        )

    def indexable_content(self, obj):
        """Return dict with indexable content for `obj`"""

        try:
            review_state = api.content.get_state(obj)
        except:
            review_state = ''

        document_id = self.document_id(obj)

        d = dict()
        d['id'] = document_id
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
        schemes = iterSchemata(obj)
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

        return d

    def indexed_content(self, obj):
        """Return the indexed content in Typesense for the given `obj`"""

        client = self.get_typesense_client()
        document_id = self.document_id(obj)

        try:
            document = (
                client.collections[self.collection]
                .documents[document_id]
                .retrieve()
            )
        except typesense.exceptions.ObjectNotFound:
            document = {}

        return document

    def document_id(self, obj):
        """Return the content id for the given `obj`"""

        site_id = api.portal.get().getId()
        obj_id = f'{site_id}-{obj.UID()}'
        return obj_id

    def document_path(self, obj):
        """Return the content path for the given `obj`"""

        return '/'.join(obj.getPhysicalPath())

    def exists_collection(self, collection):
        """Check if collection exists"""

        client = self.get_typesense_client()
        all_collections = [
            collection['name'] for collection in client.collections.retrieve()
        ]
        return collection in all_collections

    def create_collection(self):
        """Create collection"""

        client = self.get_typesense_client()
        collection = self.collection

        if self.exists_collection(collection):
            raise RuntimeError(f'Collection `{collection}` already exists')

        collection_schema = COLLECTION_SCHEMA
        collection_schema['name'] = collection

        create_response = client.collections.create(collection_schema)

    def drop_collection(self):
        """Drop collection"""

        collection = self.collection
        if self.exists_collection(collection):

            client = self.get_typesense_client()
            try:
                client.collections[collection].delete()
                LOG.info(f'Deleted Typesense collection {collection}')
            except Exception as e:
                LOG.exception(
                    f'Could not delete Typesense collection {collection}'
                )
                raise

    def collection_stats(self):
        """Get collection statistics"""

        client = self.get_typesense_client()
        return client.collections[self.collection].retrieve()

    def get_typesense_client(
        self,
    ):
        """Typesense client with full admin access"""

        api_key = api.portal.get_registry_record('api_key', ITypesenseSettings)
        return self.get_client(api_key)

    def get_typesense_search_client(self):
        """Typesense client with search access"""

        search_api_key = api.portal.get_registry_record(
            'search_api_key', ITypesenseSettings
        )
        return self.get_client(search_api_key)

    def get_client(self, api_key):
        """Get Typesense client for given API key"""

        try:
            node1_url = api.portal.get_registry_record(
                'node1_url', ITypesenseSettings
            )
            node2_url = api.portal.get_registry_record(
                'node2_url', ITypesenseSettings
            )
            node3_url = api.portal.get_registry_record(
                'node3_url', ITypesenseSettings
            )
        except (KeyError, ComponentLookupError):
            return None

        nodes = list()
        for url in (node1_url, node2_url, node3_url):
            if not url:
                continue

            f = furl.furl(url)
            nodes.append(dict(host=f.host, port=f.port, protocol=f.scheme))

        client = typesense.Client(
            {
                'api_key': api_key,
                'nodes': nodes,
                'connection_timeout_seconds': 10,
            }
        )
        return client

    def export_documents(self):
        """Export all documents of collection as JSONlines"""
        client = self.get_typesense_client()
        return client.collections[self.collection].documents.export()
