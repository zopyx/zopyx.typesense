import typesense

collection = 'typesense'

client = typesense.Client({
    'api_key': 'pnmaster',
    'nodes': [{
        'host': 'localhost',
        'port': '8108',
        'protocol': 'http'
    }],
    'connection_timeout_seconds': 2
})

coll = client.collections[collection]
import pdb; pdb.set_trace()
