import os
from logging import debug, info
import pandas as pd
from numbers import Number
import re
from math import isnan
import numpy as np

import json

from mast.core.io import APIConnector

def read_xlsx(filename: str) -> pd.DataFrame:
    Database_summary = pd.read_excel(open(filename, "rb"), sheet_name="Summary")

    # Initialize an empty list to store the data
    data_summary = []

    # Iterate through the rows
    for index, row in Database_summary.iterrows():
        # Check if the row is empty (all NaN values)
        if row.isnull().all():
            break  # Exit the loop if an empty row is encountered
        data_summary.append(row)
        
    # Convert the collected data to a new DataFrame
    experiment = pd.DataFrame(data_summary)

    # Rename the columns
    experiment.rename(columns = {
        "Building #": "id",
        "Scheme": "scheme",
        "Reference": "reference",
        "Publication year": "publication_year",
        "Short description": "description",
        "Experiment ID": "experiment_id",
        "Scale of test": "test_scale",
        "Number of simultaneous excitations": "simultaneous_excitations_nb",
        "Directions of applied excitations": "applied_excitation_directions",
        "Number of test runs": "run_results_nb",
        "Number of storeys": "storeys_nb",
        "Total building height": "total_building_height",
        "Diaphragm material": "diaphragm_material",
        "Roof material and geometry": "roof_material_geometry",
        "Type of masonry unit": "masonry_unit_type",
        "Masonry unit material": "masonry_unit_material",
        "Mortar type": "mortar_type",
        "Compressive strength of masonry": "masonry_compressive_strength",
        "Masonry walls thickness": "masonry_wall_thickness",
        "Number of wall leaves": "wall_leaves_nb",
        "Internal walls": "internal_walls",
        "Mechanical connectors present": "mechanical_connectors",
        "Activation of connectors": "connectors_activation",
        "Retrofitted": "retrofitted",
        "Application of retrofitting": "retrofitting_application",
        "Type of retrofitting": "retrofitting_type",
        "First estimated fundamental period": "first_estimated_fundamental_period",
        "Last estimated fundamental period": "last_estimated_fundamental_period",
        "Maximum horizontal PGA": "max_horizontal_pga",
        "Maximum estimated DG": "max_estimated_dg",
        "Material characterization available": "material_characterizations",
        "Associated type of test": "associated_test_types",
        "Reference for material characterization": "material_characterization_refs",
        "Experimental results reported": "experimental_results_reported",
        "Measured data openly available as digital files": "open_measured_data",
        "Link to request data": "link_to_request_data",
        "Digitalized data available": "digitalized_data",
        "Types of cracks observed": "crack_types_observed",
        "Motivation of the experimental campaign": "experimental_campaign_motivation",
        "Link to experimental paper": "link_to_experimental_paper",
        "Corresponding author": "corresponding_author_name",
    }, inplace=True)
    
    # Drop some columns
    del experiment["id"]
    del experiment["scheme"] # do not handle scheme image yet
    del experiment["run_results_nb"] # dynamically calculated

    # Split author string
    experiment[["corresponding_author_name", "corresponding_author_email"]] = experiment["corresponding_author_name"].str.rsplit("\n", n=1, expand=True)
    
    # Prepare array values
    def array_formatter(x):
        if isinstance(x, Number) and isnan(x):
            return None
        if isinstance(x, str):
            x = x.strip()
            x = re.split(r"\n|/", x)
        return x if isinstance(x, list) else [x]
    
    for col in ["applied_excitation_directions", "masonry_wall_thickness", "retrofitting_type", "material_characterizations", "material_characterization_refs", "associated_test_types", "experimental_results_reported", "crack_types_observed"]:
        experiment[col] = experiment[col].apply(array_formatter)

    # Clean number values
    def number_cleanup(x):
        rval = x
        if not isinstance(x, Number) or isnan(x):
            rval = None
        return rval
    
    for col in ["publication_year", "storeys_nb", "total_building_height", "masonry_compressive_strength", "wall_leaves_nb", "first_estimated_fundamental_period", "last_estimated_fundamental_period", "max_horizontal_pga", "max_estimated_dg"]:
        experiment[col] = experiment[col].apply(number_cleanup)
    # for some reason pandas changes None for NaN, so we need to change it back
    experiment = experiment.replace({np.nan:None})

    # Split open measures data field
    experiment["link_to_open_measured_data"] = experiment["open_measured_data"].map(lambda x: x if x.startswith("http") else None)
    
    # Clean boolean values
    def yesno_cleanup(x):
        return x != None and x != "No"
    
    for col in ["open_measured_data", "digitalized_data", "internal_walls", "retrofitted"]:
        experiment[col] = experiment[col].apply(yesno_cleanup)

    # Clean string values
    def string_cleanup(x):
        return x if isinstance(x, str) else None
    
    for col in ["experimental_campaign_motivation"]:
        experiment[col] = experiment[col].apply(string_cleanup)

    # References    
    reference = experiment[["reference", "publication_year", "link_to_experimental_paper", "corresponding_author_name", "corresponding_author_email", "link_to_request_data"]].drop_duplicates().copy()
    reference["request_data_available"] = reference["link_to_request_data"].map(lambda x: x if not x.startswith("http") else "Available on request")
    reference["link_to_request_data"] = reference["link_to_request_data"].map(lambda x: x if x.startswith("http") else None)
    reference.index = np.arange(1, len(reference)+1)

    # Experiments
    experiment["reference_id"] = experiment["reference"].map(lambda x: reference[reference["reference"] == x].index[0])
    experiment = experiment.drop(["publication_year", "link_to_experimental_paper", "corresponding_author_name", "corresponding_author_email", "link_to_request_data"], axis=1)
    experiment.index = np.arange(1, len(experiment)+1)

    # Full references
    Database_references = pd.read_excel(open(filename, "rb"), sheet_name="References", usecols="A:C", header=1)
    Database_references.drop("Excel sheet name", axis=1, inplace=True)
    Database_references.rename(columns={"Building #": "experiment_id", "Reference": "full_reference"}, inplace=True)
    full_reference = pd.merge(experiment[["reference_id"]], Database_references, left_index=True, right_on="experiment_id").drop("experiment_id", axis=1).drop_duplicates()
    reference = pd.merge(reference, full_reference, left_index=True, right_on="reference_id").drop("reference_id", axis=1)

    return experiment, reference

def do_upload(filename: str, key: str, url: str) -> None:
    """Upload a file to the MAST service

    Args:
        filename: Path to the file to upload
        key: API key to authenticate with the MAST service
        url: URL of the MAST service API
    """
    # Check if the file exists
    if not os.path.exists(filename):
        raise FileNotFoundError(f"File not found: {filename}")
    info(f"Upload {filename} to {url}")

    # Read the Excel file
    info("reading Excel file")
    experiment, reference = read_xlsx(filename)
    
    # Connect to the API
    api = APIConnector(url, key)

    ref_ids = {}

    # Write the DataFrame to the database
    info("writing references")
    for index, row in reference.iterrows():
        debug(f">>> writing reference {index}")
        #debug(f"{row.to_dict()}")
        try:
            res = api.post("/references", row.to_dict())
            #debug(f"{res}")
            ref_ids[row["reference"]] = res["id"]
            debug(f"<<< reference {index} written")
        except Exception as e:
            debug(f"<<< reference {index} not written: {e}")
    #debug(f"{ref_ids}")
    
    # Apply the reference IDs from the database
    experiment["reference_id"] = experiment["reference"].map(lambda x: int(ref_ids[x]) if x in ref_ids else None)
    experiment = experiment.drop("reference", axis=1)
    
    # Write the DataFrame to the database
    info("writing experiments")
    for index, row in experiment.iterrows():
        if not row["reference_id"] or isnan(row["reference_id"]):
            debug(f">>> NOT writing experiment {index}: {row['reference_id']}")
            continue
        debug(f">>> writing experiment {index}")
        try:
            res = api.post("/experiments", row.to_dict())
            #debug(f"{res}")
            debug(f"<<< experiment {index} written")
        except Exception as e:
            debug(f"<<< experiment {index} not written: {e}")
