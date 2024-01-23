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

    def upload_files(self, id, zipfile: str):
        return FilesService(self.conn).upload(zipfile, prefix=f"/experiments/{id}")
    
    def get_files(self, id, file: str):
        return self.conn.download(f"/experiments/{id}/files", file)
    
    def delete_files(self, id):
        return self.conn.delete(f"/experiments/{id}/files")
    
    def delete(self, id, recursive: bool = False):
        self.conn.delete(f"/experiments/{id}?recursive={recursive}")

    def list(self, params=None):
        return self.conn.get("/experiments", params=params)