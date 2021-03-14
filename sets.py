import random as rn
import json as js

class AssetSet():
    def __init__(self, jsonFile='sets.json'):
        super().__init__()
        self.lastValue = -1
        self.collection = self.build_collection(jsonFile=jsonFile)
        self.fresh = self.collection
        self.used = []

    def build_collection(self,jsonFile):
        collection = self.fromJSON(jsonFile)
        return collection

    def get_next(self):
        remaining = len(self.fresh)
        if remaining <= 1:
            n = 0
        else:
            n = rn.randrange(0,remaining)
        item = self.fresh[n]
        self.fresh.remove(item)
        if len(self.fresh) == 0:
            self.fresh = self.used
            self.used = []
        self.used.append(item)
        return item
        
    def add_asset(self,asset):
        self.collection.append(asset)

    def fromJSON(self,jsonFile):
        jsonString = open(jsonFile)
        data = js.load(jsonString)
        jsonString.close()
        return data
        