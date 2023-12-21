import typer
from logging import DEBUG, INFO, NOTSET, basicConfig
from mast.core.upload import do_upload
from mast.services.references import ReferencesService
from mast.services.experiments import ExperimentsService
from mast.core.io import APIConnector
import json
import pandas as pd
import sys

# Initialise the Typer class
app = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    pretty_exceptions_show_locals=False,
)

default_url = "https://mast-dev.epfl.ch/api"

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
    do_upload(APIConnector(url, key), filename)

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
def rm_reference(
    id: str = typer.Argument(
        ...,
        help="ID of the reference to remove"
    ),
    force: bool = typer.Option(
        False,
        help="Force the deletion, otherwise ask for confirmation",
        prompt="Are you sure you want to delete the reference?"
    ),
    recursive: bool = typer.Option(
        False,
        help="Remove the reference and all associated experiments"
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
    """Remove a reference"""
    if force:
        service = ReferencesService(APIConnector(url, key))
        service.delete(id, recursive)

@app.command()
def references(
    format: str = typer.Option(
        "json",
        help="Format of the output: json or csv"
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
    """Get the list of references"""
    service = ReferencesService(APIConnector(url, None))
    res = service.list()
    print_output(res, format, pretty)

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
def rm_experiment(
    id: str = typer.Argument(
        ...,
        help="ID of the experiment to remove"
    ),
    force: bool = typer.Option(
        False,
        help="Force the deletion, otherwise ask for confirmation",
        prompt="Are you sure you want to delete the experiment?"
    ),
    recursive: bool = typer.Option(
        False,
        help="Remove the experiment and all associated run results"
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
    """Remove an experiment"""
    if force:
        service = ExperimentsService(APIConnector(url, key))
        service.delete(id, recursive)
    
@app.command()
def experiments(
    reference: int = typer.Option(
        None,
        help="ID of the reference to filter by"
    ),
    format: str = typer.Option(
        "json",
        help="Format of the output: json or csv"
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
    print_output(res, format, pretty)


def print_output(res, format, pretty):
    """Print the output"""
    if format == "csv":
        pd.DataFrame(res).to_csv(sys.stdout, index=False, sep="\t", quotechar='"')
    else:
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

    basicConfig(level=INFO)
    app()


if __name__ == "__main__":
    main()