import os
import json
import zipfile
import tempfile
import shutil
import typer
from time import strftime
from pathlib import Path
from logging import info, warning, error

from mast.core.io import APIConnector
from mast.services.experiments import ExperimentsService
from mast.services.run_results import RunResultsService

def write_empty_file(parent, name):
  """Create an empty file if it does not exist"""
  path = os.path.join(parent, name)
  if not os.path.exists(path):
    with open(path, "w"):
        pass

def write_empty_run_files(run_ids, parent, ext):
  """Create empty files for each run id"""
  for run_id in run_ids:
    write_empty_file(parent, f"{run_id}.{ext}")

def get_3d_model_folder(experiment_folder):
  return os.path.join(experiment_folder, "3D model")

def get_period_dg_folder(experiment_folder):
  return os.path.join(experiment_folder, "Period and DG evolution")

def get_crack_maps_folder(experiment_folder):
  return os.path.join(experiment_folder, "Crack maps")

def get_global_force_displacement_curve_folder(experiment_folder):
  return os.path.join(experiment_folder, "Global force-displacement curve")

def get_shake_table_accelerations_folder(experiment_folder):
  return os.path.join(experiment_folder, "Shake-table accelerations")

def get_top_displacement_histories_folder(experiment_folder):
  return os.path.join(experiment_folder, "Top displacement histories")

def list_files_recursively(folder_path):
    paths = [] 
    for file_path in Path(folder_path).rglob('*'):
        if file_path.is_file():
            paths.append(str(file_path))
    return paths

def zip_to_temp_file(folder_path):
    # Create a temp file
    temp_file = tempfile.mkdtemp(".zip")
    
    with zipfile.ZipFile(temp_file, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for foldername, subfolders, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                arcname = os.path.relpath(file_path, folder_path)
                zip_file.write(file_path, arcname)
    
    return temp_file

def unzip_to_temp_directory(zip_file_path):
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()

    try:
        # Open the ZIP file
        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
            # Extract all contents to the temporary directory
            zip_ref.extractall(temp_dir)

        # Return the path to the temporary directory
        return temp_dir

    except Exception as e:
        print(f"Error during unzip: {e}")
        # Clean up on error
        shutil.rmtree(temp_dir)
        raise

def do_generate_repo(conn: APIConnector, folder: str, id: str = None):
  """Generates the experiment's repository structure"""
  experiment = None
  run_ids = ["1", "2", "3"]
  if id:
    experiment = ExperimentsService(conn).get(id)
    run_results = RunResultsService(conn).list({"filter": json.dumps({"experiment_id": int(id)})})
    run_ids = [run_result["run_id"] for run_result in run_results if run_result["run_id"] not in ["Initial", "Final"]]
  
  experiment_folder = os.path.expanduser(folder)

  md_folder = get_3d_model_folder(experiment_folder)
  os.makedirs(md_folder, exist_ok=True)
  write_empty_file(md_folder, "main.vtk")

  pdge_folder = get_period_dg_folder(experiment_folder)
  os.makedirs(pdge_folder, exist_ok=True)
  write_empty_file(pdge_folder, "Period_evolution.png")
  write_empty_file(pdge_folder, "DG_evolution.png")

  cm_folder = get_crack_maps_folder(experiment_folder)
  os.makedirs(cm_folder, exist_ok=True)
  write_empty_run_files(run_ids, cm_folder, "png")
  
  gfdc_folder = get_global_force_displacement_curve_folder(experiment_folder)
  os.makedirs(gfdc_folder, exist_ok=True)
  write_empty_run_files(run_ids, gfdc_folder, "txt")
  
  sta_folder = get_shake_table_accelerations_folder(experiment_folder)
  os.makedirs(sta_folder, exist_ok=True)
  write_empty_run_files(run_ids, sta_folder, "txt")
  
  tdh_folder = get_top_displacement_histories_folder(experiment_folder)
  os.makedirs(tdh_folder, exist_ok=True)
  write_empty_run_files(run_ids, tdh_folder, "txt")

  rdm_path = os.path.join(experiment_folder, "README.md")
  if not os.path.exists(rdm_path):
    with open(rdm_path, "w") as f:
      if experiment:
        f.write(f"# {experiment['experiment_id'] if experiment['experiment_id'] else id}\n")
      else:
        f.write(f"# _experiment_id_\n")
      if experiment:
        if experiment["description"]:
          f.write(f"\n{experiment['description']}\n")
      else:
        f.write(f"\n_experiment_description_\n")
      f.write(f"\n## Generated on {strftime('%Y-%m-%d %H:%M:%S')}\n")

  return experiment_folder


def do_validate_repo(conn: APIConnector, folder_or_zip: str, id: str = None):
  warnings = []
  errors = []
  experiment_folder = os.path.expanduser(folder_or_zip)
  
  if os.path.isfile(folder_or_zip):
    if folder_or_zip.endswith(".zip"):
      experiment_folder = unzip_to_temp_directory(folder_or_zip)
      dirs = [f.path for f in os.scandir(experiment_folder) if f.is_dir()]
      if len(dirs) == 1:
          experiment_folder = dirs[0]
    else:
      errors.append(f"Experiment repository must be either a folder or a zip file")
      return warnings, errors
  
  experiment = None
  run_ids = []
  if id:
    try:
      experiment = ExperimentsService(conn).get(id)
      run_results = RunResultsService(conn).list({"filter": json.dumps({"experiment_id": int(id)})})
      run_ids = [run_result["run_id"] for run_result in run_results if run_result["run_id"] not in ["Initial", "Final"]]
    except:
      errors.append(f"Experiment with id {id} does not exist")
      return warnings, errors

  md_folder = get_3d_model_folder(experiment_folder)
  if os.path.exists(md_folder):
    vtks = [f.path for f in os.scandir(md_folder) if f.is_file() and (f.path.endswith(".vtk") or f.path.endswith(".vtp"))]
    if not vtks:
      warnings.append(f"Missing at least one .vtk or .vtp file: '3D model'")
  else:
    warnings.append(f"Missing folder: '3D model'")
  
  pdge_folder = get_period_dg_folder(experiment_folder)
  if os.path.exists(pdge_folder):
    pngs = [f.path for f in os.scandir(pdge_folder) if f.is_file() and f.path.endswith(".png")]
    if not pngs:
      warnings.append(f"Missing at least one .png file: 'Period and DG evolution'")
  else:
    warnings.append(f"Missing folder: 'Period and DG evolution'")
  
  cm_folder = get_crack_maps_folder(experiment_folder)
  if os.path.exists(cm_folder):
    for run_id in run_ids:
      if not os.path.exists(os.path.join(cm_folder, f"{run_id}.png")):
        warnings.append(f"Missing file: 'Crack maps/{run_id}.png'")
  else:
    warnings.append(f"Missing folder: 'Crack maps'")
  
  gfdc_folder = get_global_force_displacement_curve_folder(experiment_folder)
  if os.path.exists(gfdc_folder):
    for run_id in run_ids:
      if not os.path.exists(os.path.join(gfdc_folder, f"{run_id}.txt")):
        warnings.append(f"Missing file: 'Global force-displacement curve/{run_id}.txt'")
  else:
    warnings.append(f"Missing folder: 'Global force-displacement curve'")  

  sta_folder = get_shake_table_accelerations_folder(experiment_folder)
  if os.path.exists(sta_folder):
    for run_id in run_ids:
      if not os.path.exists(os.path.join(sta_folder, f"{run_id}.txt")):
        warnings.append(f"Missing file: 'Shake-table accelerations folder/{run_id}.txt'")
  else:
    warnings.append(f"Missing folder: 'Shake-table accelerations'")

  tdh_folder = get_top_displacement_histories_folder(experiment_folder)
  if os.path.exists(tdh_folder):
    for run_id in run_ids:
      if not os.path.exists(os.path.join(tdh_folder, f"{run_id}.txt")):
        warnings.append(f"Missing file: 'Top displacement histories/{run_id}.txt'")
  else:
    warnings.append(f"Missing folder: 'Top displacement histories'")

  rdm_path = os.path.join(experiment_folder, "README.md")
  if not os.path.exists(rdm_path):
    warnings.append(f"README.md file does not exist")

  if folder_or_zip.endswith(".zip"):
    # remove temp folder
    shutil.rmtree(experiment_folder)

  return warnings, errors

def do_upload_repo(conn: APIConnector, file: str, id: str = None, force: bool = False):
    in_file = os.path.expanduser(file)
    is_temp = False
    if not os.path.isfile(in_file):
      # make a zip file
      is_temp = True
      in_file = zip_to_temp_file(in_file)
    elif not in_file.endswith(".zip"):
      error("Not a zip file, aborting upload")
      return

    warnings, errors = do_validate_repo(conn, os.path.expanduser(file), id)
    if errors:
        for err in errors:
            error(err)
        info("Aborting upload")
        return

    if warnings:
        for warn in warnings:
            warning(warn)
        if not force:
            typer.confirm("Do you want to continue?", abort=True)

    res = ExperimentsService(conn).upload_files(id, in_file)
    if is_temp:
      os.remove(in_file)
    return res
