import os
import json
import zipfile
import tempfile
import shutil
import typer
from time import strftime
from pathlib import Path
from logging import info, warning, error
from importlib import resources as impresources

from mast import templates
from mast.core.io import APIConnector
from mast.services.experiments import ExperimentsService
from mast.services.run_results import RunResultsService

def write_empty_file(parent, name):
  """Create an empty file if it does not exist"""
  path = os.path.join(parent, name)
  if not os.path.exists(path):
    if name.endswith(".png"):
      missing_file = impresources.files(templates) / "missing.png"
      shutil.copy(missing_file, path)
    else:  
        with open(path, "w"):
            pass

def write_empty_run_files(run_ids, parent, ext):
  """Create empty files for each run id"""
  for run_id in run_ids:
    write_empty_file(parent, f"{run_id}.{ext}")

def get_3d_model_folder(experiment_folder):
  return os.path.join(experiment_folder, "3D model")

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
    temp_file = tempfile.mktemp(".zip")
    
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
  experiment_folder = os.path.expanduser(folder)
  lic_file = impresources.files(templates) / "License-cc-by-sa.md"
  
  # test folder
  test_folder = os.path.join(experiment_folder, "test")
  os.makedirs(test_folder, exist_ok=True)
  
  run_ids = ["1", "2", "3"]
  if id:
    experiment = ExperimentsService(conn).get(id)
    run_results = RunResultsService(conn).list({"filter": json.dumps({"experiment_id": int(id)})})
    run_ids = [run_result["run_id"] for run_result in run_results if run_result["run_id"] not in ["Initial", "Final"]]
    
  cm_folder = get_crack_maps_folder(test_folder)
  os.makedirs(cm_folder, exist_ok=True)
  write_empty_run_files(run_ids, cm_folder, "png")
  
  gfdc_folder = get_global_force_displacement_curve_folder(test_folder)
  os.makedirs(gfdc_folder, exist_ok=True)
  write_empty_run_files(run_ids, gfdc_folder, "txt")
  
  sta_folder = get_shake_table_accelerations_folder(test_folder)
  os.makedirs(sta_folder, exist_ok=True)
  write_empty_run_files(run_ids, sta_folder, "txt")
  
  tdh_folder = get_top_displacement_histories_folder(test_folder)
  os.makedirs(tdh_folder, exist_ok=True)
  write_empty_run_files(run_ids, tdh_folder, "txt")

  rdm_path = os.path.join(test_folder, "README.md")
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

  lic_path = os.path.join(test_folder, "License.md")
  if not os.path.exists(lic_path):
    shutil.copy(lic_file, lic_path)

  # plan folder
  plan_folder = os.path.join(experiment_folder, "plan")
  os.makedirs(plan_folder, exist_ok=True)
  write_empty_file(plan_folder, "plan.png")
  
  prdm_path = os.path.join(plan_folder, "README.md")
  if not os.path.exists(prdm_path):
    shutil.copy(rdm_path, prdm_path)
  lic_path = os.path.join(plan_folder, "License.md")
  if not os.path.exists(lic_path):
    shutil.copy(lic_file, lic_path)
  
  # model folder
  model_folder = os.path.join(experiment_folder, "model")
  opensees_folder = os.path.join(model_folder, "OpenSees")
  os.makedirs(opensees_folder, exist_ok=True)
  
  mrdm_path = os.path.join(model_folder, "README.md")
  if not os.path.exists(mrdm_path):
    shutil.copy(rdm_path, mrdm_path)
  lic_path = os.path.join(model_folder, "License.md")
  if not os.path.exists(lic_path):
    shutil.copy(lic_file, lic_path)
  write_empty_file(model_folder, "scheme.png")
  write_empty_file(model_folder, "geometry.vtk")

  return experiment_folder


def do_validate_repo(conn: APIConnector, folder_or_zip: str, type: str, id: str = None):
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
  
  if id:
    try:
      ExperimentsService(conn).get(id)
    except:
      errors.append(f"Experiment with id {id} does not exist")
      return warnings, errors
  
  if type == "test":
    run_ids = []
    if id:
      try:
        run_results = RunResultsService(conn).list({"filter": json.dumps({"experiment_id": int(id)})})
        run_ids = [run_result["run_id"] for run_result in run_results if run_result["run_id"] not in ["Initial", "Final"]]
      except:
        errors.append(f"Experiment with id {id} does not exist")
        return warnings, errors
    
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
  
  elif type == "model":
    path = os.path.join(experiment_folder, "geometry.vtk")
    if not os.path.exists(path):
      warnings.append(f"geometry.vtk file does not exist")
      
    path = os.path.join(experiment_folder, "scheme.png")
    if not os.path.exists(path):
      warnings.append(f"scheme.png file does not exist")

  path = os.path.join(experiment_folder, "License.md")
  if not os.path.exists(path):
    warnings.append(f"License.md file does not exist")
  
  path = os.path.join(experiment_folder, "README.md")
  if not os.path.exists(path):
    warnings.append(f"README.md file does not exist")

  if folder_or_zip.endswith(".zip"):
    # remove temp folder
    shutil.rmtree(experiment_folder)

  return warnings, errors

def do_upload_repo(conn: APIConnector, file: str, id: str = None, type: str = "test", force: bool = False):
    in_file = os.path.expanduser(file)
    is_temp = False
    if not os.path.isfile(in_file):
      # make a zip file
      is_temp = True
      in_file = zip_to_temp_file(in_file)
    elif not in_file.endswith(".zip"):
      error("Not a zip file, aborting upload")
      return

    warnings, errors = do_validate_repo(conn, os.path.expanduser(file), type, id)
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

    res = ExperimentsService(conn).upload_files(id, type, in_file)
    if is_temp:
      os.remove(in_file)
    return res
