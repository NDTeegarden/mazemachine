import random as rn
import json as js

class AssetSet():
    def __init__(self, jsonFile='sets.json'):
        super().__init__()
        self.lastValue = -1
        self.build_collection(jsonFile=jsonFile)

    def build_collection(self,jsonFile):
        self.collection = self.fromJSON(jsonFile)

    def get_next(self):
        last = self.lastValue
        if last < 0:
            n = 0
        else:
            n = rn.randrange(1,len(self.collection))
            if n == last:
                n = 0
        item = self.collection[n]
        self.lastValue = n
        return item
        
    def add_asset(self,asset):
        self.collection.append(asset)

    def fromJSON(self,jsonFile):
        jsonString = open(jsonFile)
        data = js.load(jsonString)
        jsonString.close()
        return data
        