from mastdb.core.io import APIConnector

class RunResultsService:
    def __init__(self, conn: APIConnector):
        self.conn = conn

    def get(self, id):
        return self.conn.get(f"/run_results/{id}")

    def create(self, data):
        return self.conn.post("/run_results", data=data)

    def update(self, id, data):
        return self.conn.put(f"/run_results/{id}", data=data)

    def delete(self, id):
        return self.conn.delete(f"/run_results/{id}")

    def list(self, params=None):
        return self.conn.get("/run_results", params=params)