import pprint
import furl
import plone.api
import typesense
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zope.component import queryMultiAdapter
from zopyx.typesense.interfaces import ITypesenseSettings

def index_content(context, event):

    try:
        collection = plone.api.portal.get_registry_record("collection", ITypesenseSettings)
        api_key = plone.api.portal.get_registry_record("api_key", ITypesenseSettings)
        node1_url = plone.api.portal.get_registry_record("node1_url", ITypesenseSettings)
        node2_url = plone.api.portal.get_registry_record("node2_url", ITypesenseSettings)
        node3_url = plone.api.portal.get_registry_record("node3_url", ITypesenseSettings)
    except:
        return

    serializer = queryMultiAdapter((event.object, event.object.REQUEST), ISerializeToJson)
    if not serializer:
        return
    try:
        result = serializer()
    except:
        return

    pprint.pprint(result)

    nodes = list()
    for url in (node1_url, node2_url, node3_url):
        if not url:
            continue

        f = furl.furl(url)
        nodes.append(dict(
                host=f.host,
                port=f.port,
                protocol=f.scheme
                ))


    client = typesense.Client({
    'api_key': api_key,
    'nodes': nodes,
    'connection_timeout_seconds': 2
    })


    try:
        client.collections[collection].delete()
    except Exception as e:
        pass

    try:
        create_response = client.collections.create({
            "name": "typesense",
            "fields": [
                {"name": "path", "type": "string"},
                {"name": "id", "type": "string"},
                {"name": "title", "type": "string"},
                {"name": "description", "type": "string"},
                {"name": "text", "type": "string"},
                {"name": "language", "type": "string", "facet": True},
                {"name": "portal_type", "type": "string", "facet": True},
                {"name": "review_state", "type": "string", "facet": False},
            ],
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
        print(create_response)
    except:
        pass




    retrieve_response = client.collections[collection].retrieve()
    print(retrieve_response)

    try:
        review_state = plone.api.content.get_state(context)
    except:
        review_state = ''

    d = dict()
    d['id'] = context.getId()
    d['title'] = context.Title()
    d['description'] = context.Description()
    d['language'] = context.Language()
    d['portal_type'] = context.portal_type
    d['text'] = "xxxxx"
    d['review_state'] = review_state
    d['path'] = '/'.join(context.getPhysicalPath())
    pprint.pprint(d)

    response = client.collections[collection].documents.create(d)
    print(response)
