# EESD - MAST

MAST (MAsonry Shake-Table) is a comprehensive database and collaborative resource for advancing seismic assessment of unreinforced masonry buildings.

Visit [EESD lab at EPFL](https://www.epfl.ch/labs/eesd/).

This tool is a command-line interface to the MAST API, for data upload, extraction and analysis.

Usage:

```
mast --help
```

## Buildings Database

The buildings folder contains the data for provisionning the MAST web application, using the mast CLI.

```
.
├── <Building ID>_XXXX
│   ├── model
│   │   ├── OpenSees
│   │   │   └── <...>
│   │   ├── geometry.vtk
│   │   ├── scheme.png
│   │   ├── License.md
│   │   └── README.md
│   ├── plan
│   │   ├── <some name>.png
│   │   ├── License.md
│   │   └── README.md
│   └── test
│       ├── Crack maps
│       │   ├── <run ID>.png
│       │   └── <...>.png
│       ├── Global force-displacement curve
│       │   ├── <run ID>.txt
│       │   └── <...>.txt
│       ├── Shake-table accelerations
│       │   ├── <run ID>.txt
│       │   └── <...>.txt
│       ├── Top displacement histories
│       │   ├── <run ID>.txt
│       │   └── <...>.txt
│       ├── License.md
│       └── README.md
├── Readme.md
└── Shake_Table_Tests_Database_XXXXX.xlsx
```

### Excel database

#### Building experiments, references and run results

The .xlsx file from which the building experiments (experiment description, reference and run results) are to be uploaded is to be explicitly specified.

Command to update the database of building experiments, reference and run results:

```
mast upload --key xxxxxxx 00_MAST_Database/Shake_Table_Tests_Database_XXXXX.xlsx
```

#### Building numerical models

The .xlsx file from which the building numerical models are to be uploaded is to be explicitly specified, and MUST happen after the building experiments have been uploaded (see above). 

Command to update the database of building experiments, reference and run results:

```
mast upload-models --key xxxxxxx 00_MAST_Database/.xlsx
```

### Building data folders

Provide one data folder per building. The naming conventions are:

1. Building folder name starts with Building's ID (leading zeros are ok). The subsequent part of the name (after _) is ignored.
2. In each folder, the data files are organized as follows:
  * `model`, contains the numerical model files
    * `geometry.vtk` is the main 3D model, additional VTK files (with any name) can be provided.
    * `scheme.png` is the main model image that will appear in the Buildings page. Other png files for additional model views, can be provided (with any names).
    * Any folder, with like the OpenSees example can be provided.
    * README.md, recommended and optional
    * License.md, recommended and optional
  * `plan`, contains the plan view files
    * Any png file name.
    * README.md, recommended and optional
    * License.md, recommended and optional
  * `test`, contains the test files
    * `Crack maps`, png files, named by the corresponding run ID
    * `Global force-displacement curve`, txt files, named by the corresponding run ID
    * `Shake-table accelerations`, txt files, named by the corresponding run ID
    * `Top displacement histories`, txt files, named by the corresponding run ID
    * Any folder, with like can be provided.
    * README.md, recommended and optional
    * License.md, recommended and optional


Command to update all the database files:

```
mast upload-repo-bulk --key xxxxxxx 00_MAST_Database
```

Command to update a specific type of database files of a specific Building:

```
mast upload-repo --key xxxxxxx --type model 1 00_MAST_Database/001_Beyer_2015/model
```

Command to remove a specific type of database files of a specific Building:

```
mast rm-repo --key xxxxxxx --type model 1
```

In order to help with the setup and the validation of an experiment's local repository, use the commands:

```
mast generate-repo --help
```

To validate an existing experiment data files repository, use the command:

```
mast validate-repo --help
```

To download an experiment data files repository into a local folder, use the command:

```
mast download-repo --help
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
