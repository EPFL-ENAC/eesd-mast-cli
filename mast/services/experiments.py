import json
from mast.core.io import APIConnector
from mast.services.files import FilesService

class ExperimentsService:
    def __init__(self, conn: APIConnector):
        self.conn = conn

    def get(self, id):
        return self.conn.get(f"/experiments/{id}")

    def create(self, data):
        return self.conn.post("/experiments", data=data)

    def update(self, id, data):
        return self.conn.put(f"/experiments/{id}", data=data)

    def upload_scheme_file(self, id, file: str):
        return FilesService(self.conn).upload(file, ws=f"/experiments/{id}/scheme")
        
    def upload_files(self, id, type: str, zipfile: str):
        return FilesService(self.conn).upload(zipfile, ws=f"/experiments/{id}/{type}")
    
    def get_files(self, id, type: str, file: str):
        return self.conn.download(f"/experiments/{id}/{type}", file)
    
    def delete_files(self, id, type: str):
        return self.conn.delete(f"/experiments/{id}/{type}")
    
    def delete_run_results(self, id):
        return self.conn.delete(f"/experiments/{id}/run_results")
    
    def delete(self, id, recursive: bool = False):
        self.conn.delete(f"/experiments/{id}?recursive={recursive}")

    def list(self, params=None):
        return self.conn.get("/experiments", params=params)
    
    def createOrUpdate(self, data):
        """Create or update an experiment, using its building identifier"""
        try:
            filter = {"building_id": data["building_id"]}
            params = {"filter": json.dumps(filter)}
            res = self.list(params=params)
            if len(res) > 0:
                data["id"] = res[0]["id"]
                data.pop("scheme", None) # images will be uploaded separately
                data.pop("files", None)
                data.pop("models", None)
                return self.update(res[0]["id"], data)
            else:
                return self.create(data)
        except Exception as e:
            return self.create(data)
        