from .huey_tasks import ts_index, ts_unindex
from datetime import datetime
from plone import api
from plone.app.textfield import RichText
from plone.dexterity.utils import iterSchemata
from zope.interface.interfaces import ComponentLookupError
from zope.schema import getFields
from zope.component import getAdapter
from zope.component import ComponentLookupError
from zopyx.typesense import _, LOG
from zopyx.typesense.interfaces import ITypesenseSettings
from zopyx.typesense.interfaces import ITypesenseIndexDataProvider

import json
import furl
from datetime import datetime
import typesense
import zope.schema
import html_text


def html2text(html):
    tree = html_text.parse_html(html)
    return html_text.extract_text(tree)


class API:
    @property
    def collection(self):
        """Return collection name from registry"""
        collection = api.portal.get_registry_record("collection", ITypesenseSettings)
        return collection

    def index_document(self, obj):
        """Index document `obj`"""

        data = self.indexable_content(obj)
        if not data:
            return 

        ts_index(
            ts_client=self.get_typesense_client(),
            collection=self.collection,
            data=data,
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


        # review states
        review_states_to_index = api.portal.get_registry_record("review_states_to_index", ITypesenseSettings)
        review_states_to_index = [s.strip() for s in review_states_to_index.split("\n") if s.strip()]

        ignore_review_state = False
        try:
            review_state = api.content.get_state(obj)
        except:
            review_state = ""
            ignore_review_state = True

        if not ignore_review_state and not review_state in review_states_to_index:
            # don't index content without proper review state
            return 
        
        # language
        default_language = api.portal.get_default_language()
        language = obj.Language() or default_language

        document_id = self.document_id(obj)

        d = dict()
        d["id"] = document_id
        d["id_original"] = obj.getId()
        d["title"] = obj.Title()
        d["description"] = obj.Description()
        d["language"] = language
        d["portal_type"] = obj.portal_type
        d["review_state"] = review_state
        d["path"] = self.document_path(obj)
        d["created"] = obj.created().ISO8601()
        d["modified"] = obj.modified().ISO8601()
        d["effective"] = obj.effective().ISO8601()
        d["expires"] = obj.expires().ISO8601()
        d["subject"] = obj.Subject()
        d["uid"] = obj.UID()
        d["document_type_order"] = 0
        d["_indexed"] = datetime.utcnow().isoformat()

        # indexable text content
        indexable_text = []

        fields = {}
        schemes = iterSchemata(obj)
        for schema in schemes:
            fields.update(getFields(schema))

        for name, field in fields.items():
            if isinstance(field, RichText):
                text = getattr(obj, name)
                if isinstance(text, str):
                    indexable_text.append(text)
                else:
                    if text and text.output:
                        indexable_text.append(html2text(text.output))
            elif isinstance(field, (zope.schema.Text, zope.schema.TextLine)):
                text = getattr(obj, name)
                indexable_text.append(text)

        indexable_text = [text for text in indexable_text if text]
        indexable_text = " ".join(indexable_text)
        d["text"] = indexable_text

        # Check if there is an adapter for the given content type interface
        # implementing ITypesenseIndexDataProvider for modifying the index data
        # dict.

        try:
            adapter = getAdapter(obj, ITypesenseIndexDataProvider)
        except ComponentLookupError:
            adapter = None

        if adapter:
            d = adapter.get_indexable_content(d)

        return d

    def indexed_content(self, obj):
        """Return the indexed content in Typesense for the given `obj`"""

        client = self.get_typesense_client()
        document_id = self.document_id(obj)

        try:
            document = (
                client.collections[self.collection].documents[document_id].retrieve()
            )
        except typesense.exceptions.ObjectNotFound:
            document = {}

        return document

    def document_id(self, obj):
        """Return the content id for the given `obj`"""

        site_id = api.portal.get().getId()
        obj_id = f"{site_id}-{obj.UID()}"
        return obj_id

    def document_path(self, obj):
        """Return the content path for the given `obj`"""

        site_path = "/".join(api.portal.get().getPhysicalPath())
        obj_path = "/".join(obj.getPhysicalPath())
        rel_path = obj_path.replace(site_path, "")
        rel_path = rel_path.lstrip("/")
        return rel_path

    def exists_collection(self, collection):
        """Check if collection exists"""

        client = self.get_typesense_client()
        all_collections = [
            collection["name"] for collection in client.collections.retrieve()
        ]
        return collection in all_collections

    def create_collection(self):
        """Create collection"""

        client = self.get_typesense_client()
        collection = self.collection

        if self.exists_collection(collection):
            raise RuntimeError(f"Collection `{collection}` already exists")

        collection_schema = api.portal.get_registry_record(
            "collection_schema", ITypesenseSettings
        )
        collection_schema = json.loads(collection_schema)
        collection_schema["name"] = collection

        client.collections.create(collection_schema)
        LOG.info(f"Created Typesense collection {collection}")

    def drop_collection(self):
        """Drop collection"""

        collection = self.collection
        if self.exists_collection(collection):

            client = self.get_typesense_client()
            try:
                client.collections[collection].delete()
                LOG.info(f"Deleted Typesense collection {collection}")
            except Exception as e:
                LOG.exception(f"Could not delete Typesense collection {collection}")
                raise

    def collection_stats(self):
        """Get collection statistics"""

        client = self.get_typesense_client()
        try:
            result = client.collections[self.collection].retrieve()
        except Exception as e:
            LOG.error("Unable to fetch Typesense stats", exc_info=True)
            return {}

        result["created_at_str"] = datetime.fromtimestamp(
            result["created_at"]
        ).isoformat()
        return result

    def get_typesense_client(
        self,
    ):
        """Typesense client with full admin access"""
        return self.get_client(self.api_key)

    def get_typesense_search_client(self):
        """Typesense client with search access"""
        return self.get_client(self.search_api_key)

    @property
    def search_api_key(self):
        """Return search API key"""
        return api.portal.get_registry_record("search_api_key", ITypesenseSettings)

    @property
    def api_key(self):
        """Return admin API key"""
        return api.portal.get_registry_record("api_key", ITypesenseSettings)

    def get_client(self, api_key):
        """Get Typesense client for given API key"""

        if not api_key:
            raise ValueError(_("No Typesense API key(s) configured"))

        client = typesense.Client(
            {
                "api_key": api_key,
                "nodes": self.nodes,
                "connection_timeout_seconds": 10,
            }
        )
        return client

    @property
    def nodes(self):
        """Return a list of Typesense nodes (used by the search UI)"""

        try:
            node1_url = api.portal.get_registry_record("node1_url", ITypesenseSettings)
            node2_url = api.portal.get_registry_record("node2_url", ITypesenseSettings)
            node3_url = api.portal.get_registry_record("node3_url", ITypesenseSettings)
        except (KeyError, ComponentLookupError):
            return None

        nodes = list()
        for url in (node1_url, node2_url, node3_url):
            if not url:
                continue

            f = furl.furl(url)
            nodes.append(dict(host=f.host, port=f.port, protocol=f.scheme))

        return nodes

    def export_documents(self, format="jsonl"):
        """Export all documents of collection as JSONlines"""
        client = self.get_typesense_client()
        result = client.collections[self.collection].documents.export()
        if format == "jsonl":
            return result
        else:
            # JSON
            result = [json.loads(jline) for jline in result.splitlines()]
            return json.dumps(result, indent=2)

    def search(self, query, per_page=25, page=1):

        client = self.get_typesense_client()
        search_params = {
            "q": query,
            "query_by": "text",
            "per_page": per_page,
            "page": page,
            #            'sort_by': 'id2:desc',
            #            'facet_by': ['language,area,document_type,societies,specifications_str,specifications2_str,topic_str']
        }

        LOG.info(search_params)
        result = client.collections[self.collection].documents.search(search_params)
        result["pages"] = (
            int(result["found"] / result["request_params"]["per_page"]) + 1
        )
        return result

    def snapshot(self):
        """Snapshot typesense database.
        Cavecat: If Typesense is running with a Docker container,
        the snapshot will be created inside the container unless you configure
        a volume mapping.
        """

        client = self.get_typesense_client()
        snapshot_path = f"{self.collection}-{datetime.utcnow().isoformat()}.snapshot"
        client.operations.perform("snapshot", {"snapshot_path": snapshot_path})
        return snapshot_path

    def cluster_data(self):
        """Return metrics, stats etc. from Typesense"""

        client = self.get_typesense_client()

        try:
            # cluster
            metrics = client.metrics.retrieve()
            stats = client.stats.retrieve()
            health = client.health.retrieve()
            return dict(metrics=metrics, health=health, stats=stats)
        except AttributeError:
            # standalone
            return None
