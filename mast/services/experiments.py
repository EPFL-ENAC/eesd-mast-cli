from mast.core.io import APIConnector

class ExperimentsService:
    def __init__(self, conn: APIConnector):
        self.conn = conn

    def get(self, id):
        return self.conn.get(f"/experiments/{id}")

    def create(self, data):
        return self.conn.post("/experiments", data=data)

    def update(self, id, data):
        return self.conn.put(f"/experiments/{id}", data=data)

    def delete(self, id):
        return self.conn.delete(f"/experiments/{id}")

    def list(self, params=None):
        return self.conn.get("/experiments", params=params)