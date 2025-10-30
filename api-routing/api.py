from fastapi import FastAPI

class Api(object):
    def __init__(self):
        self.api = FastAPI()
        self._routing()

    def _routing(self):
        self.api.get('/') (self.index)
        
    def index(self):
        return {"message": 123}