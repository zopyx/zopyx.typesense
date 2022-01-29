import typer
import furl
import typesense
import pprint

app = typer.Typer()


@app.command()
def collections(
        url=typer.Option(...),
        api_key=typer.Option(...)):
    typer.echo("Collections...")

    f = furl.furl(url)
    nodes = [dict(host=f.host, port=f.port, protocol=f.scheme)]
    client = typesense.Client(dict(api_key=api_key, nodes=nodes))
    result = client.collections.retrieve()
    for row in result:
        print(f"{row['name']:20s} {row['num_documents']}")


@app.command()
def delete(username: str):
    typer.echo(f"Deleting user: {username}")

if __name__ == "__main__":
    app()
