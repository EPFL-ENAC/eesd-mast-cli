# EESD - MAST

MAST (MAsonry Shake-Table) is a comprehensive database and collaborative resource for advancing seismic assessment of unreinforced masonry buildings.

Visit [EESD lab at EPFL](https://www.epfl.ch/labs/eesd/).

This tool is a command-line interface to the MAST API, for data upload, extraction and analysis.

## Experiments Database

### Excel Database Upload

To upload experiments with their reference article and test runs summaries, use the command:

```
mast upload --help
```

### Experiment Repository Conventions

Each experiment comes with its set of test results as files. The experiment's repository conventions are:

```
.
├── 3D model
│   └── main.vtk (or main.vtp)
│
├── Crack maps
│   ├── <Run ID>.png
│   └── ...
│
├── Global force-displacement curve
│   ├── <Run ID>.txt
│   └── ...
│
├── Period and DG evolution
│   ├── DG_evolution.png
│   └── Period_evolution.png
│
├── Shake-table accelerations
│   ├── <Run ID>.txt
│   └── ...
│
└── Top displacement histories
    ├── <Run ID>.txt
    └── ...
```

where:

* The 3D model can be in multiple files in VTK format (both `.vtk` or `.vtp` file extensions are supported)
* `Run ID` is one of the run results identifiers declared in the database.
* `.png` files are images.
* `.txt` files are data files in tab separated values format.

In order to help with the setup and the validation of an experiment's local repository, use the commands:

```
mast generate-repo --help
```

To validate an existing experiment data files repository, use the command:

```
mast validate-repo --help
```

To upload an experiment data files local folder or zip archive, use the command:

```
mast upload-repo --help
```

To download an experiment data files repository into a local folder, use the command:

```
mast download-repo --help
```

To remove the experiment data files, use the command:

```
mast rm-repo --help
```

## Development

Setup package dependencies

```
poetry install
```

Run command line

```
poetry run mast --help
```
