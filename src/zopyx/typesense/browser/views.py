from Products.Five.browser import BrowserView
from zope.event import notify
from zope.interface.interfaces import ComponentLookupError
from zope.lifecycleevent import ObjectModifiedEvent
from zopyx.typesense import _, LOG
from zopyx.typesense.api import API
from zopyx.typesense.interfaces import ITypesenseSettings

import furl
import json
import plone.api
import pprint
import time
import typesense


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

    def export_documents(self):
        """Export all documents from current collection as JSONLines"""

        ts_api = API()
        result = ts_api.export_documents()

        self.request.response.setHeader("content-type", "application/json")
        self.request.response.setHeader(
            "content-disposition",
            f"attachment; filename={ts_api.collection}.jsonl",
        )
        return result

    def collection_information(self):
        """Retrieve Collection information"""

        ts_api = API()
        return ts_api.collection_stats()

    def reindex_all(self):
        """Reindex all"""

        ts = time.time()

        ts_api = API()
        ts_api.drop_collection()
        ts_api.create_collection()

        catalog = plone.api.portal.get_tool("portal_catalog")
        brains = catalog()
        num_brains = len(list(brains))
        for i, brain in enumerate(brains):
            if i % 1000 == 0:
                LOG.info(f"{i + 1}/{num_brains} objects indexed")
            obj = brain.getObject()
            ts_api.index_document(obj)

        duration = time.time() - ts
        LOG.info(
            f"All content reindexed ({num_brains} items), duration {duration:.2f} seconds"
        )

        portal = plone.api.portal.get()
        plone.api.portal.show_message(
            _(
                "All content submitted for reindexing. Results may/will show up delayed depending on the amount of documents!"
            ),
            request=self.request,
        )
        self.request.response.redirect(portal.absolute_url() + "/@@typesense-admin")
