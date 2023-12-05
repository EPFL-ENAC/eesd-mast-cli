from mast.core.io import APIConnector

class ReferencesService:
    def __init__(self, conn: APIConnector):
        self.conn = conn

    def get(self, id):
        return self.conn.get(f"/references/{id}")

    def create(self, data):
        return self.conn.post("/references", data=data)

    def update(self, id, data):
        return self.conn.put(f"/references/{id}", data=data)

    def delete(self, id):
        return self.conn.delete(f"/references/{id}")

    def list(self, params=None):
        return self.conn.get("/references", params=params)