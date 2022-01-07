from huey import SqliteHuey

from . import LOG

huey = SqliteHuey(filename='/tmp/demo.db')


def create_collection(ts_client, collection):

    collections = [c["name"] for c in ts_client.collections.retrieve()]
    if not collection :
        create_response = ts_client.collections.create({
            "name": collection,
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

@huey.task()
def ts_index(ts_client, collection, data, document_id, document_path):

    LOG.info(f"Indexing {document_id} : {document_path}")

    try:
        response = ts_client.collections[collection].documents.upsert(data)
    except typesense.exception.ObjectNotFound:
        create_collection(ts_client, collection)
        response = ts_client.collections[collection].documents.upsert(data)



@huey.task()
def ts_unindex(ts_client, collection, document_id, document_path):

    LOG.info(f"Unindexing {document_id} : {document_path}")

    try:
        response = ts_client.collections[collection].documents[document_id].delete()
    except typesense.exception.ObjectNotFound:
        create_collection(ts_client, collection)
        response = ts_client.collections[collection].documents[document_id].delete()
