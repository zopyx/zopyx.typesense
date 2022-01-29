import typer
import furl
import typesense
import pprint

app = typer.Typer()


DEFAULT_SCHEMA = {
  "name": "companies",
  "fields": [
    {"name": ".*", "type": "auto" }
  ]
}


@app.command()
def list(
        url=typer.Option(...),
        api_key=typer.Option(...)):

    f = furl.furl(url)
    nodes = [dict(host=f.host, port=f.port, protocol=f.scheme)]
    client = typesense.Client(dict(api_key=api_key, nodes=nodes))
    result = client.collections.retrieve()
    for row in result:
        print(f"{row['name']:20s} {row['num_documents']}")

@app.command()
def create(
        collection: str,
        url=typer.Option(...),
        api_key=typer.Option(...)):

    f = furl.furl(url)
    nodes = [dict(host=f.host, port=f.port, protocol=f.scheme)]
    client = typesense.Client(dict(api_key=api_key, nodes=nodes))

    schema = DEFAULT_SCHEMA.copy()
    schema["name"] = collection
    client.collections.create(schema)

@app.command()
def drop(
        collection: str,
        url=typer.Option(...),
        api_key=typer.Option(...)):

    f = furl.furl(url)
    nodes = [dict(host=f.host, port=f.port, protocol=f.scheme)]
    client = typesense.Client(dict(api_key=api_key, nodes=nodes))

    client.collections[collection].delete()

@app.command()
def delete(username: str):
    typer.echo(f"Deleting user: {username}")

if __name__ == "__main__":
    app()
