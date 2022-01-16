from .api import API
from plone import api
from zopyx.typesense import LOG
from zopyx.typesense.interfaces import ITypesenseSettings

import time


def can_index():
    """Check if the Typesense registry settings are available"""

    try:
        api.portal.get_registry_record("collection", ITypesenseSettings)
    except:
        return False

    enabled = api.portal.get_registry_record("enabled", ITypesenseSettings)
    if not enabled:
        site_id = api.portal.get().getId()
        LOG.warning(f"Typesense indexing is disabled for Plone site {site_id}")
    return enabled


def remove_content(context, event):
    """Async removal of content"""

    if not can_index():
        return

    ts = time.time()
    ts_api = API()
    ts_api.unindex_document(context)
    duration = (time.time() - ts) * 1000
    LOG.info(
        f"Unindexing {context.getId(), context.absolute_url(1)}, {duration:.3f} ms"
    )


def update_content(context, event):
    """Async indexing of content"""

    if not can_index():
        return

    ts = time.time()
    ts_api = API()
    ts_api.index_document(context)
    duration = (time.time() - ts) * 1000
    LOG.info(f"Indexing {context.getId(), context.absolute_url(1)}, {duration:.3f} ms")
