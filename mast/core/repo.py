import os
import json
from time import strftime
from pathlib import Path

from mast.core.io import APIConnector
from mast.services.files import FilesService
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


def do_validate_repo(conn: APIConnector, folder: str, id: str = None):
  warnings = []
  errors = []
  experiment_folder = os.path.expanduser(folder)
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
    if not os.path.exists(os.path.join(md_folder, "main.vtk")):
      errors.append(f"'3D model' folder exists but does not contain the main.vtk file")
  else:
    warnings.append(f"'3D model' folder does not exist")
  
  pdge_folder = get_period_dg_folder(experiment_folder)
  if os.path.exists(pdge_folder):
    if not os.path.exists(os.path.join(pdge_folder, "Period_evolution.png")):
      errors.append(f"'Period and DG evolution' folder exists but does not contain the Period_evolution.png file")
    if not os.path.exists(os.path.join(pdge_folder, "DG_evolution.png")):
      errors.append(f"'Period and DG evolution' folder exists but does not contain the DG_evolution.png file")
  else:
    warnings.append(f"'Period and DG evolution' folder does not exist")
  
  cm_folder = get_crack_maps_folder(experiment_folder)
  if os.path.exists(cm_folder):
    for run_id in run_ids:
      if not os.path.exists(os.path.join(cm_folder, f"{run_id}.png")):
        errors.append(f"'Crack maps' folder exists but does not contain the {run_id}.png file")
  else:
    warnings.append(f"'Crack maps' folder does not exist")
  
  gfdc_folder = get_global_force_displacement_curve_folder(experiment_folder)
  if os.path.exists(gfdc_folder):
    for run_id in run_ids:
      if not os.path.exists(os.path.join(gfdc_folder, f"{run_id}.txt")):
        errors.append(f"'Global force-displacement curve' folder exists but does not contain the {run_id}.txt file")
  else:
    warnings.append(f"'Global force-displacement curve' folder does not exist")  

  sta_folder = get_shake_table_accelerations_folder(experiment_folder)
  if os.path.exists(sta_folder):
    for run_id in run_ids:
      if not os.path.exists(os.path.join(sta_folder, f"{run_id}.txt")):
        errors.append(f"'Shake-table accelerations folder' exists but does not contain the {run_id}.txt file")
  else:
    warnings.append(f"'Shake-table accelerations' folder does not exist")

  tdh_folder = get_top_displacement_histories_folder(experiment_folder)
  if os.path.exists(tdh_folder):
    for run_id in run_ids:
      if not os.path.exists(os.path.join(tdh_folder, f"{run_id}.txt")):
        errors.append(f"'Top displacement histories' folder exists but does not contain the {run_id}.txt file")
  else:
    warnings.append(f"'Top displacement histories' folder does not exist")

  rdm_path = os.path.join(experiment_folder, "README.md")
  if not os.path.exists(rdm_path):
    warnings.append(f"README.md file does not exist")

  return warnings, errors


def do_upload_repo(conn: APIConnector, zipfile: str, id: str = None):
  experiment = ExperimentsService(conn).get(id)
  
  return FilesService(conn).upload(zipfile, prefix=f"/experiments/{id}")