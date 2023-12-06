import os
from mast.core.io import APIConnector

class FilesService:
    def __init__(self, conn: APIConnector):
        self.conn = conn

    def upload(self, path):
        # Specify the paths to the files to upload
        file_paths = [path]

        # Open each file in binary mode and send them as part of the request
        file_tuples = [("files", (os.path.basename(f), open(f, "rb"), "application/octet-stream")) for f in file_paths]
        files = dict(file_tuples)

        return self.conn.upload("/files", files=files)

    def delete(self, id):
        return self.conn.delete(f"/files/{id}")
