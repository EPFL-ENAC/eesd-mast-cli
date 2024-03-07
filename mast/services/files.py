import os
from mast.core.io import APIConnector

class FilesService:
    def __init__(self, conn: APIConnector):
        self.conn = conn

    def upload(self, path, root = None, ws = "/files"):
        # Specify the paths to the files to upload
        file_paths = [path] if isinstance(path, str) else path

        # Open each file in binary mode and send them as part of the request
        files = []
        for f in file_paths:
            files.append(("files", (self._get_file_name(f, root), open(f, "rb"), self._get_content_type(f))))

        return self.conn.upload(ws, files=files)

    def delete(self, id, ws = "/files"):
        return self.conn.delete(f"{ws}/{id}")

    def _get_file_name(self, path, root = None):
        if root is None:
            return os.path.basename(path)
        return os.path.relpath(path, root)

    def _get_content_type(self, path):
        if path.endswith(".png"):
            return "image/png"
        elif path.endswith(".jpg"):
            return "image/jpeg"
        elif path.endswith(".webp"):
            return "image/webp"
        elif path.endswith(".vtk") or path.endswith(".vtp"):
            return "application/x-vtk"
        elif path.endswith(".txt"):
            return "text/plain"
        elif path.endswith(".csv"):
            return "text/csv"
        elif path.endswith(".zip"):
            return "application/zip"
        else:
            return "application/octet-stream"