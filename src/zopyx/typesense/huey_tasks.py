from huey import SqliteHuey

from . import LOG

huey = SqliteHuey(filename='/tmp/demo.db')

@huey.task()
def ts_index(ts_client, collection, data, document_id, document_path):
    LOG.info(f"Indexing {document_id} : {document_path}")
    response = ts_client.collections[collection].documents.upsert(data)


@huey.task()
def ts_unindex(ts_client, collection, document_id, document_path):
    LOG.info(f"Unindexing {document_id} : {document_path}")
    response = ts_client.collections[collection].documents[document_id].delete()
