import json
import os.path
from functools import reduce
import random

class DataPreparator:
    
    def _load_json(self, filename):
        print('Loading %s', filename)
        with open(filename, encoding="utf8") as f:
            inputStr = f.read()
            return json.loads(inputStr)
    
    def _save_json(self, filename, data):
        with open(filename, 'w') as f:
            jsonData = json.dumps(data, indent=2)
            f.write(jsonData)
        print('Saved %s' % filename)
    
    def _reducer(self, x, y):
        for k in y.keys():
            if not k in x:
                x[k] = []
            x[k].append(y[k])
        return x
    
    def _process(self, data):
        if self.transformer:
            self.transformer.fit(data)
            processed = self.transformer.transform(data)
        if self.validator:
            processed = list(filter(self.validator, processed))
        processed = reduce(self._reducer, processed, {})
        return processed

    def _shuffle(self, data):
        random.Random(self._seed).shuffle(data)
    
    def __init__(self, transformer, validator, force_save=False, randomSeed=1):
        self.transformer = transformer
        self.validator = validator
        self._force_save = force_save
        self._seed = randomSeed
    
    def prepare(self, inputFile, outputFile):
        if self._force_save or not os.path.isfile(outputFile):
            inputJson = self._load_json(inputFile)
            self._shuffle(inputJson)
            data = self._process(inputJson)
            self._save_json(outputFile, data)
            return data
        else:
            print('%s exists' % outputFile)
            return self._load_json(outputFile)