from Products.Five.browser import BrowserView

from zopyx.typesense import _, LOG
from zopyx.typesense.api import API

import json
import gzip
import os
import plone.api
import time


class View(BrowserView):
    def recreate_collection(self):

        ts_api = API()

        ts_api.drop_collection()
        ts_api.create_collection()

        LOG.info(f"Created Typesense collection {ts_api.collection}")

        portal = plone.api.portal.get()
        plone.api.portal.show_message(
            _("Typesense collection dropped and recreated"),
            request=self.request,
        )
        self.request.response.redirect(portal.absolute_url() + "/@@typesense-admin")

    def indexed_content(self):
        """Return indexed content for current context object"""

        ts_api = API()
        document = ts_api.indexed_content(self.context)
        return document

    def export_documents(self, format="jsonl"):
        """Export all documents from current collection as JSONLines"""

        ts_api = API()
        result = ts_api.export_documents(format)

        self.request.response.setHeader("content-type", f"application/{format}")
        self.request.response.setHeader(
            "content-disposition",
            f"attachment; filename={ts_api.collection}.{format}",
        )
        return result

    def collection_information(self):
        """Retrieve Collection information"""

        ts_api = API()
        return ts_api.collection_stats()

    def reindex_all(self, batch_size=100):
        """Reindex all"""

        ts = time.time()
        ts_api = API()
        ts_api.drop_collection()
        ts_api.create_collection()

        catalog = plone.api.portal.get_tool("portal_catalog")
        brains = catalog()
        num_brains = len(list(brains))
        for i, brain in enumerate(brains):
            if i % batch_size == 0:
                LOG.info(f"{i + 1}/{num_brains} objects indexed")
            obj = brain.getObject()
            ts_api.index_document(obj)

        duration = time.time() - ts
        LOG.info(
            f"All content submitted for reindexing ({num_brains} items), duration {duration:.2f} seconds"
        )

        portal = plone.api.portal.get()
        plone.api.portal.show_message(
            _(
                "All content submitted for reindexing. Results may/will show up delayed depending on the amount of documents!"
            ),
            request=self.request,
        )
        self.request.response.redirect(portal.absolute_url() + "/@@typesense-admin")

    def search_result(self):
        """Search UI for admin view"""
        ts_api = API()
        result = ts_api.search(
            query=self.request.form.get("query"), page=self.request.form.get("page", 1)
        )
        return result

    def import_demo_content(self):

        from plone.app.textfield.value import RichTextValue

        portal = plone.api.portal.get()

        if "news" in portal.objectIds():
            plone.api.content.delete(portal.news)

        data_folder = plone.api.content.create(
            container=portal, type="Folder", id="news", title="news"
        )

        fn = os.path.dirname(__file__) + "/de-news.json"
        news = json.load(open(fn))
        for n in news:
            text = RichTextValue(n["text"], "text/html", "text/html")
            doc = plone.api.content.create(
                type="News Item",
                container=data_folder,
                title=n["title"],
                text=text,
                language="de",
            )
            plone.api.content.transition(doc, "publish")

        plone.api.portal.show_message(
            _("Sample content import into folder /news"),
            request=self.request,
        )
        self.request.response.redirect(portal.absolute_url() + "/@@typesense-admin")

    def snapshot(self):
        """Create a snapshot of the Typesense internal database"""

        ts_api = API()
        snapshot_name = ts_api.snapshot()

        portal = plone.api.portal.get()
        plone.api.portal.show_message(
            _(f"Snapshot taken ({snapshot_name})"),
            request=self.request,
        )
        self.request.response.redirect(portal.absolute_url() + "/@@typesense-admin")

    def cluster_data(self):
        """Return metrics, stats from Typesense"""

        ts_api = API()
        return ts_api.cluster_data()

    def search_settings(self):
        """Typesense settings returned as JSON for dynamic search UI"""

        ts_api = API()

        settings = dict()
        settings["collection"] = ts_api.collection
        settings["api_key"] = ts_api.search_api_key
        settings["nodes"] = ts_api.nodes
        settings["query_by"] = "title,text"

        self.request.response.setHeader("content-type", "application/json")
        return json.dumps(settings)
