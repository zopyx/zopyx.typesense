"""
Demo adapter for IDocument.

This adapter has no serious functionality other than demonstrating how to
implement a custom indexing data provider. The implementation of this adapter
just returns the indexable data for IDocument 1:1 without further
modifications.

See api.COLLECTION_SCHEMA for the list of available fields and implementation
of api.indexable_content() for details.
"""


class DocumentIndexer:
    """Typesense indexer for IDocument"""

    def __init__(self, context):
        self.context = context

    def get_indexable_content(self, indexable_content):
        """Return indexable content for IDocument"""

        # you can modify the dict with the data to be indexed according to your
        # own needs.

        # indexable_content["text"] = "foo bar"
        return indexable_content
