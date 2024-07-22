# EESD - MAST

MAST (MAsonry Shake-Table) is a comprehensive database and collaborative resource for advancing seismic assessment of unreinforced masonry buildings.

The associated public website is [https://masonrydb.epfl.ch/](https://masonrydb.epfl.ch/).

Visit [EESD lab at EPFL](https://www.epfl.ch/labs/eesd/).

This tool is a command-line interface to the MAST database API, for data upload, extraction and analysis.

Installation:

```
pip install mastdb
```

Usage:

```
mastdb --help
```

## Buildings Database

The buildings folder contains the data for provisionning the MAST web application, using the `mastdb` command line interface.

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
mastdb upload --key xxxxxxx 00_MAST_Database/Shake_Table_Tests_Database_XXXXX.xlsx
```

#### Building numerical models

The .xlsx file from which the building numerical models are to be uploaded is to be explicitly specified, and MUST happen after the building experiments have been uploaded (see above). 

Command to update the database of building experiments, reference and run results:

```
mastdb upload-models --key xxxxxxx 00_MAST_Database/Modeling\ assumptions.xlsx
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
mastdb upload-repo-bulk --key xxxxxxx 00_MAST_Database
```

Command to update a specific type of database files of a specific Building:

```
mastdb upload-repo --key xxxxxxx --type model 1 00_MAST_Database/001_Beyer_2015/model
```

Command to remove a specific type of database files of a specific Building:

```
mastdb rm-repo --key xxxxxxx --type model 1
```

In order to help with the setup and the validation of an experiment's local repository, use the commands:

```
mastdb generate-repo --help
```

To validate an existing experiment data files repository, use the command:

```
mastdb validate-repo --help
```

To download an experiment data files repository into a local folder, use the command:

```
mastdb download-repo --help
```

## Cookbook

The following recipes will help site maintainers to update, delete or add content to the MAST database.

### What is the official MAST database website?

The official MAST database website is located at [https://masonrydb.epfl.ch/](https://masonrydb.epfl.ch/). The website is for humans exploring the content of the database. For the site maintainers, the address to be provided to the `mastdb` command line is [https://masonrydb.epfl.ch/api](https://masonrydb.epfl.ch/api).

### Is there a MAST database website that I can use as a playground?

Yes, from the EPFL intranet, you can use the website [https://mast-dev.epfl.ch/](https://mast-dev.epfl.ch/) as a playground. Similarly to the official website, the address to provide for updating database content is [https://mast-dev.epfl.ch/api](https://mast-dev.epfl.ch/api).

If you are not sure about the kind of operation and/or the data content you want to send to the database, it is recommended to use this website as a playground.

### What are experiments, run results and numerical models? Where are the buildings?

An experiment is an experiment made on a building. Resulting from this experiment, there are run results. Similarly, a numerical model is a numerical model of a building. In the database, there is no building per-say: both experiments and numerical models refer to their associated building by an identifier (1, 2, 3 etc.), then make sure this identifier is used consistently in the database operations.

### How can I add/update an experiment of a building?

The content updated is based on the Excel file that was originally defined. You can refer to it to add or modify the content of the database: 

* Reference: define the associated paper information, that can be referred by several buildings.
* Building: each building has an identifier that you provide (which can be different from the record identifier in the database). Make sure that this identifier is unique, as it is to used to perform updates or deletions.
* Tests results: use the table conventions from the Excel file (do not change column names).

### How can I delete an experiment of a building?

You can delete a building by its identifier. It will also delete the associated files and test results.

### How can I delete only the files a building?

You can delete the files of a building by its identifier and the type of files (plan, model or test).

### How can I upload the various type of files?

1. Make sure the building exists in the database (not just in the Excel file).
2. When it is the first time files are uploaded for that building, use the `mastdb generate-repo` command in a directory of your choice. This command will prepopulate folders hierarchy, with dummy files. More specifically, pay attention to the test results file names, as proper naming is required to link observed data and crack images to the test results defined in the database.
3. It is highly recommended to provide README and License files.

### How can I add/update a numerical model?

Just like for the experiments, adding/updating numerical models of buildings is to be done using an Excel file. See the original 'Modeling assumptions.xlsx' file as a reference. Make sure to not modify the field names, and also to be consistent with the identification of the building (use same building id as for the experiments) and with the reference name.

### How can I delete a numerical model?

You can delete a numerical model by its building identifier.

### What is the 'key' in the command arguments?

One need to authenticate itself to perform 'write' operations (add, update or delete). The MAST database uses a simple authentication mechanism based on a API key (to be requested to ENAC IT4R team).

### Where are the data originally used to provision the database?

See the [MAST DB project data folder](https://epflch.sharepoint.com/:f:/r/sites/ENAC-IT/Documents%20partages/Research%20IT/Advanced%20Services/0145%20%E2%80%93%20MAST%20Open%20DB/Data/00_MAST_Database?csf=1&web=1&e=brnmh1) (requires proper access, ask ENAC IT4R team).

## Development

Setup package dependencies

```
poetry install
```

Run command line

```
poetry run mastdb --help
```
