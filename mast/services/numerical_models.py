from mast.core.io import APIConnector

class NumericalModelsService:
    def __init__(self, conn: APIConnector):
        self.conn = conn

    def get(self, id):
        return self.conn.get(f"/numerical_models/{id}")

    def create(self, data):
        return self.conn.post("/numerical_models", data=data)

    def update(self, id, data):
        return self.conn.put(f"/numerical_models/{id}", data=data)

    def delete(self, id):
        return self.conn.delete(f"/numerical_models/{id}")

    def list(self, params=None):
        return self.conn.get("/numerical_models", params=params)