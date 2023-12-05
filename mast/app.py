import typer
from logging import DEBUG, INFO, basicConfig
from mast.core.upload import do_upload
from mast.services.references import ReferencesService
from mast.services.experiments import ExperimentsService
from mast.core.io import APIConnector
import json

# Initialise the Typer class
app = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    pretty_exceptions_show_locals=False,
)

default_url = "http://127.0.0.1:8000"

@app.command()
def upload(
    filename: str = typer.Argument(
        ...,
        help="Path to the Excel file to import"
    ),
    key: str = typer.Option(
        ...,
        help="API key to authenticate with the MAST service"
    ),
    url: str = typer.Option(
        default_url, 
        help="URL of the MAST service API to connect to"
    )
    ) -> None:
    """Import a Excel file with metadata to the database

    The Excel file must have the following columns: x, y, z
    """
    do_upload(filename, key, url)

#
# References
#

@app.command()
def reference(
    id: str = typer.Argument(
        ...,
        help="ID of the reference to retrieve"
    ),
    url: str = typer.Option(
        default_url,
        help="URL of the MAST service API to connect to"
    ),
    pretty: bool = typer.Option(
        False,
        help="Pretty-print the JSON output"
    )
    ) -> None:
    """Get a reference article"""
    service = ReferencesService(APIConnector(url, None))
    res = service.get(id)
    print_json(res, pretty)

@app.command()
def references(
    url: str = typer.Option(
        default_url,
        help="URL of the MAST service API to connect to"
    ),
    pretty: bool = typer.Option(
        False,
        help="Pretty-print the JSON output"
    )
    ) -> None:
    """Get the list of references"""
    service = ReferencesService(APIConnector(url, None))
    res = service.list()
    print_json(res, pretty)

#
# Experiments
#

@app.command()
def experiment(
    id: str = typer.Argument(
        ...,
        help="ID of the experiment to retrieve"
    ),
    url: str = typer.Option(
        default_url,
        help="URL of the MAST service API to connect to"
    ),
    pretty: bool = typer.Option(
        False,
        help="Pretty-print the JSON output"
    )
    ) -> None:
    """Get an experiment"""
    service = ExperimentsService(APIConnector(url, None))
    res = service.get(id)
    print_json(res, pretty)

@app.command()
def experiments(
    reference: int = typer.Option(
        None,
        help="ID of the reference to filter by"
    ),
    url: str = typer.Option(
        default_url,
        help="URL of the MAST service API to connect to"
    ),
    pretty: bool = typer.Option(
        False,
        help="Pretty-print the JSON output"
    )
    ) -> None:
    """Get the list of experiments"""
    service = ExperimentsService(APIConnector(url, None))
    filter = None
    if reference:
        filter = {"reference_id": reference}
    params = None
    if filter:
        params = {"filter": json.dumps(filter)}
    res = service.list(params=params)
    print_json(res, pretty)


def print_json(res, pretty):
    """Print the JSON response"""
    if pretty:
        print(json.dumps(res, sort_keys=True, indent=4))
    else:
        print(json.dumps(res))

def main() -> None:
    """The main function of the application

    Used by the poetry entrypoint.
    """

    basicConfig(level=DEBUG)
    app()


if __name__ == "__main__":
    main()