"""
The default Typesense collection schema
"""

import json


COLLECTION_SCHEMA = {
    "name": None,
    "fields": [
        {"name": "path", "type": "string"},
        {"name": "id", "type": "string"},
        {"name": "title", "type": "string"},
        {"name": "description", "type": "string"},
        {"name": "headlines", "type": "string"},
        {"name": "text", "type": "string"},
        {"name": "language", "type": "string", "facet": True},
        {"name": "portal_type", "type": "string", "facet": True},
        {"name": "review_state", "type": "string", "facet": True},
        {"name": "subject", "type": "string[]", "facet": True},
        {"name": "created", "type": "string", "facet": False},
        {"name": "modified", "type": "string", "facet": False},
        {"name": "effective", "type": "string", "facet": False},
        {"name": "expires", "type": "string", "facet": False},
        {"name": "document_type_order", "type": "int32"},
        {"name": "_indexed", "type": "string"},
        {"name": "all_paths", "type": "string[]", "facet": False},
    ],
    "default_sorting_field": "document_type_order",
    "token_separators": ["-"],
    "attributesToSnippet": [
        "title",
        "description",
        "text:20",
    ],
    "attributesToHighlight": [
        "title",
        "description",
        "text:20",
    ],
}


COLLECTION_SCHEMA_JSON = json.dumps(COLLECTION_SCHEMA, indent=2)

# CRLF separated list of review_states to be indexes
DEFAULT_REVIEW_STATES_TO_INDEX = "published"
