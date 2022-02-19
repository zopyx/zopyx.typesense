import furl
import os
import pprint
import typer
import typesense


app = typer.Typer()


DEFAULT_SCHEMA = {"name": "companies", "fields": [{"name": ".*", "type": "auto"}]}

DEFAULT_URL = os.environ.get("TS_URL")
DEFAULT_API_KEY = os.environ.get("TS_API_KEY")


@app.command()
def list(url=typer.Option(DEFAULT_URL), api_key=typer.Option(DEFAULT_API_KEY)):

    f = furl.furl(url)
    nodes = [dict(host=f.host, port=f.port, protocol=f.scheme)]
    client = typesense.Client(dict(api_key=api_key, nodes=nodes))
    result = client.collections.retrieve()
    for row in result:
        print(f"{row['name']:20s} {row['num_documents']}")


@app.command()
def create(
    collection: str,
    url=typer.Option(DEFAULT_URL),
    api_key=typer.Option(DEFAULT_API_KEY),
):

    f = furl.furl(url)
    nodes = [dict(host=f.host, port=f.port, protocol=f.scheme)]
    client = typesense.Client(dict(api_key=api_key, nodes=nodes))

    schema = DEFAULT_SCHEMA.copy()
    schema["name"] = collection
    client.collections.create(schema)


@app.command()
def drop(
    collection: str,
    url=typer.Option(DEFAULT_URL),
    api_key=typer.Option(DEFAULT_API_KEY),
):

    f = furl.furl(url)
    nodes = [dict(host=f.host, port=f.port, protocol=f.scheme)]
    client = typesense.Client(dict(api_key=api_key, nodes=nodes))

    client.collections[collection].delete()


if __name__ == "__main__":
    app()
