"""
Indexing adapter via Apache Tika for File content
"""


from plone import api
from zopyx.typesense.interfaces import ITypesenseSettings

import os
import tempfile
import tika
import tika.parser

from .. import LOG

tika.initVM()

class FileIndexer:
    """Typesense indexer for IDocument"""

    def __init__(self, context):
        self.context = context

    def get_indexable_content(self, indexable_content):
        """Return indexable content for IFile"""

        # index content with Tika, if available
        tika_url = api.portal.get_registry_record("tika_url", ITypesenseSettings)
        if not tika_url:
            return indexable_content

        # save indexable content to temporary file
        tmp_fn = tempfile.mktemp()
        with open(tmp_fn, "wb") as fp:
            fp.write(self.context.file.data)

        # send temporary file to Apache Tika
        try:
            parsed = tika.parser.from_file(tmp_fn, serverEndpoint=tika_url)
        except Exception as e:
            LOG.exception("Unable to interact with Tika", exc_info=True)
            raise 
        finally:
            os.unlink(tmp_fn)

        indexable_content["text"] += parsed["content"]
        return indexable_content
