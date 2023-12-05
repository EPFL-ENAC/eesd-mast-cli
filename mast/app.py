import typer
from logging import DEBUG, INFO, basicConfig
from mast.core.upload import do_upload

# Initialise the Typer class
app = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    pretty_exceptions_show_locals=False,
)

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
        "http://127.0.0.1:8000",
        #"http://localhost:8000/api", 
        help="URL of the MAST service API to connect to"
    )
    ) -> None:
    """Import a Excel file with metadata to the database

    The Excel file must have the following columns: x, y, z
    """
    do_upload(filename, key, url)


@app.command()
def goodbye(name: str, formal: bool = False):
    if formal:
        print(f"Goodbye Ms. {name}. Have a good day.")
    else:
        print(f"Bye {name}!")


def main() -> None:
    """The main function of the application

    Used by the poetry entrypoint.
    """

    basicConfig(level=DEBUG)
    app()


if __name__ == "__main__":
    main()