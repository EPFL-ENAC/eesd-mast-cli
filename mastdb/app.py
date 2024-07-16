import typer
import json
import os
from logging import INFO, basicConfig, info, warning, error
from mastdb.core.utils import print_json, print_output
from mastdb.core.upload import do_upload, do_upload_models
from mastdb.core.repo import do_generate_repo, do_validate_repo, do_upload_repo
from mastdb.services.references import ReferencesService
from mastdb.services.experiments import ExperimentsService
from mastdb.services.run_results import RunResultsService
from mastdb.services.numerical_models import NumericalModelsService
from mastdb.core.io import APIConnector

# Initialise the Typer class
app = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    pretty_exceptions_show_locals=False,
)

#default_url = "https://mast-dev.epfl.ch/api"
default_url = "http://localhost:8000"

#
# Data upload
#

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
    ),
    images: bool = typer.Option(
        True,
        help="Upload thumbnail images"
    ),
    dry_run: bool = typer.Option(
        False,
        help="Dry run, do not upload to the database, just print read data"
    ),
    ) -> None:
    """Import an Excel file with metadata to the database. References and experiments will be created or updated.
    """
    do_upload(APIConnector(url, key), filename, images, dry_run)

@app.command()
def upload_models(
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
    ),
    dry_run: bool = typer.Option(
        False,
        help="Dry run, do not upload to the database, just print read data"
    ),
    ) -> None:
    """Import an Excel file with metadata to the database. Numerical models will be created or updated.
    """
    do_upload_models(APIConnector(url, key), filename, dry_run)
    
@app.command()
def generate_repo(
    folder: str = typer.Argument(
        ...,
        help="Path to the folder where experiment's file repository are to be generated"
    ),
    id: str = typer.Option(
        None,
        help="ID of the experiment to retrieve to prepopulate the experiment files repository"
    ),
    url: str = typer.Option(
        default_url, 
        help="URL of the MAST service API to connect to"
    )
    ) -> None:
    """Generates the experiment's file repository structure.

    If the experiment ID is provided, the experiment's metadata will be used to generate the README.md file
    and folders will be filled in with the empty expected run result files.
    """
    try:
        output = do_generate_repo(APIConnector(url, None), folder, id)
        info(f"Folder generated: {output}")
    except Exception as e:
        try:
            msg = json.loads(str(e))
            if "detail" in msg:
                error(msg["detail"])
            else:
                error(e)
        except:
            error(e)

@app.command()
def validate_repo(
    file: str = typer.Argument(
        ...,
        help="Path to the file where experiment's files are located, can be a folder or a zip file"
    ),
    type: str = typer.Option(
        "test",
        help="Type of the file to upload: test, model or plan"
    ),
    id: str = typer.Option(
        None,
        help="ID of the experiment to retrieve to validate the experiment files repository"
    ),
    url: str = typer.Option(
        default_url,
        help="URL of the MAST service API to connect to"
    )
    ) -> None:
    """Validates the experiment's file repository structure.
    """
    warnings, errors = do_validate_repo(APIConnector(url, None), file, type, id)
    if warnings:
        for warn in warnings:
            warning(warn)
    if errors:
        for err in errors:
            error(err)

@app.command()
def upload_repo(
    id: str = typer.Argument(
        ...,
        help="ID of the experiment to link with"
    ),
    file: str = typer.Argument(
        ...,
        help="Path to the file where experiment's files are located, can be a folder or a zip file"
    ),
    type: str = typer.Option(
        "test",
        help="Type of the file to upload: test, model or plan"
    ),
    force: bool = typer.Option(
        False,
        help="Force the upload despite warnings, otherwise ask for confirmation"
    ),
    key: str = typer.Option(
        ...,
        help="API key to authenticate with the MAST service"
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
    """Upload the experiment's file repository.
    """
    experiment = do_upload_repo(APIConnector(url, key), file, id, type, force)
    print_json(experiment, pretty)

@app.command()
def download_repo(
    id: str = typer.Argument(
        ...,
        help="ID of the experiment which files are to be downloaded"
    ),
    type: str = typer.Option(
        "test",
        help="Type of the file to download: test, model or plan"
    ),
    file: str = typer.Option(
        ...,
        help="Path to the local zip file where experiment's files are to be written"
    ),
    url: str = typer.Option(
        default_url, 
        help="URL of the MAST service API to connect to"
    )
    ) -> None:
    """Delete the experiment's file repository.
    """
    ExperimentsService(APIConnector(url, None)).get_files(id, type, file)

@app.command()
def rm_repo(
    id: str = typer.Argument(
        ...,
        help="ID of the experiment which files are to be deleted"
    ),
    type: str = typer.Option(
        "test",
        help="Type of the file to download: test, model or plan"
    ),
    force: bool = typer.Option(
        False,
        help="Force the deletion, otherwise ask for confirmation",
        prompt="Are you sure you want to delete the experiment's files?"
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
    """Delete the experiment's file repository.
    """
    if force:
        ExperimentsService(APIConnector(url, key)).delete_files(id, type)

@app.command()
def upload_repo_bulk(
    file: str = typer.Argument(
        ...,
        help="Path to the file where experiments' folders are located"
    ),
    type: str = typer.Option(
        None,
        help="Type of the file to download: test, model or plan"
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
    """Bulk upload of the experiments' files repositories. Experiment ID is guessed from the folder name. Expected subfolders are 'test', 'model' and 'plan'.
    """
    subfolders = [f.path for f in os.scandir(file) if f.is_dir()]
    #print(subfolders)
    ids = [os.path.basename(f).split("_")[0].lstrip('0') for f in subfolders]
    #print(ids)
    if not type:
        type = ["test", "model", "plan"]
    else:
        type = [type]
    
    for i, id in enumerate(ids):
        for t in type:
            type_folder = os.path.join(subfolders[i], t)
            if not os.path.exists(type_folder):
                warning(f"Folder {type_folder} not found, skipping")
                # ExperimentsService(APIConnector(url, key)).delete_files(id, t)
                continue
            info(f"Uploading {t} files for experiment {id} from {type_folder}")
            ExperimentsService(APIConnector(url, key)).delete_files(id, t)
            do_upload_repo(APIConnector(url, key), type_folder, id, t, True)
    

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
        help="Format of the output: json, csv or tsv"
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
        help="Format of the output: json, csv or tsv"
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

@app.command()
def run_results(
    experiment: int = typer.Option(
        None,
        help="ID of the experiment to filter by"
    ),
    format: str = typer.Option(
        "json",
        help="Format of the output: json, csv or tsv"
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
    """Get the list of some experiment's test run results"""
    service = RunResultsService(APIConnector(url, None))
    filter = None
    if experiment:
        filter = {"experiment_id": experiment}
    params = None
    if filter:
        params = {"filter": json.dumps(filter)}
    res = service.list(params=params)
    print_output(res, format, pretty)


@app.command()
def numerical_models(
    experiment: int = typer.Option(
        None,
        help="ID of the experiment to filter by"
    ),
    format: str = typer.Option(
        "json",
        help="Format of the output: json, csv or tsv"
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
    """Get the some experiment's numerical models"""
    service = NumericalModelsService(APIConnector(url, None))
    filter = None
    if experiment:
        filter = {"experiment_id": experiment}
    params = None
    if filter:
        params = {"filter": json.dumps(filter)}
    res = service.list(params=params)
    print_output(res, format, pretty)


@app.command()
def numerical_model(
    id: str = typer.Argument(
        ...,
        help="ID of the experiment to filter by"
    ),
    format: str = typer.Option(
        "json",
        help="Format of the output: json, csv or tsv"
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
    """Get the the experiment's numerical model"""
    service = ExperimentsService(APIConnector(url, None))
    res = service.get_numerical_model(id)
    print_output(res, format, pretty)



def main() -> None:
    """The main function of the application

    Used by the poetry entrypoint.
    """

    basicConfig(level=INFO)
    app()


if __name__ == "__main__":
    main()