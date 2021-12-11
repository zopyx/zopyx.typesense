import pprint
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

result = client.collections.retrieve()
pprint.pprint(result)
