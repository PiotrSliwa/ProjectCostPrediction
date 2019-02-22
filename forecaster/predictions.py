from data_preparator import DataPreparator

from sklearn.feature_extraction.text import *
from sklearn.pipeline import Pipeline
from sklearn.model_selection import *
from sklearn.feature_selection import *
from sklearn.linear_model import *
from sklearn.naive_bayes import *
from sklearn.neural_network import *
from sklearn.preprocessing import *
from sklearn import *
from sklearn.base import TransformerMixin
from sklearn.dummy import *
from sklearn.svm import *
from sklearn.ensemble import *
from sklearn.tree import *
from sklearn.metrics import *


import random
import html
import re
from pprint import pprint
import numpy
import scipy
import pandas

def create_thresholds(c=[0]):
    # return [numpy.percentile(c, 25), numpy.percentile(c, 50), numpy.percentile(c, 75)]
    return [numpy.percentile(c, 50)]

class InputTransformer(TransformerMixin):
    def _get_cost(self, elem):
        return elem["additions"] + elem["deletions"] + len(elem["comments"]) * 10

    def fit(self, data):
        c = list(map(self._get_cost, data))
        self.thresholds = create_thresholds(c)
    
    def _classify(self, value):
        for i, t in enumerate(self.thresholds):
            if value < t:
                return i
        return len(self.thresholds)

    def _transform_elem(self, elem):
        base = [elem['title'], elem['body']]
        comments = list(map(lambda x: x["body"], elem["comments"]))
        doc = list(map(lambda x: x if x != None else "", base + comments))
        cost = self._classify(self._get_cost(elem))
        return {
            "input": doc,
            "output": cost
        }

    def transform(self, data):
        return list(map(self._transform_elem, data))


def validator(elem):
    # return elem["output"] > 0
    return True


class ReplacingAccumulator:
    def __init__(self, replaceStr=''):
        self.arr = []
        self.replaceStr = replaceStr
    def __call__(self, m):
        r = m.group(0)
        self.arr.append(r)
        return self.replaceStr

REGEX_URL = r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)'
REGEX_PATHS = r'(?u)\b(?:[\w\.\-\#]+[/][\w\.\-\#]+)+\b'
REGEX_WORDS = r'(?u)\b\w\w+\b'

def subAndAcc(s, regex):
    acc = ReplacingAccumulator()
    r = re.sub(regex, acc, s)
    return (r, acc.arr)

def cleanToken(token):
    if re.match(r'[a-zA-Z]', token) == None:
        return None
    return token

def preprocessor(doc):
    joined = " ".join(doc)
    r = joined.replace("\n", ' ')
    r = r.replace("\r", ' ')
    r = re.sub(r'\s{2,}', ' ', r)
    return r

def complexTokenizer(s):
    r = s
    (r, urls) = subAndAcc(r, REGEX_URL)
    (r, paths) = subAndAcc(r, REGEX_PATHS)
    (r, words) = subAndAcc(r, REGEX_WORDS)
    # return filter(lambda x: x != None, map(cleanToken, urls + paths + words))
    return urls + paths + words

def wordTokenier(s):
    (r, words) = subAndAcc(s, REGEX_WORDS)
    return words

def calcWeight(arr):
    s = numpy.sort(arr)
    return s[-1] if s[-2] == 0 else s[-1] - s[-2]

def selectFeatures(x, y):
    cx = scipy.sparse.coo_matrix(x)
    freqs = []
    for i in range(0, x.shape[1]):
        freqs.append([0] * (len(create_thresholds()) + 1))
    for i,j,v in zip(cx.row, cx.col, cx.data):
        freqs[j][y[i]] += v
    d = list(map(calcWeight, freqs))
    return (d, None)

def runCase(data_inputs, data_outputs):
    pipeline = Pipeline([
        ('vect', TfidfVectorizer(tokenizer=complexTokenizer, preprocessor=preprocessor)),
        # ('sel', SelectPercentile(selectFeatures)),
        ('clf', SVC(kernel='linear')),
        # ('clf', MLPClassifier())
        # ('clf', AdaBoostClassifier())
    ])

    parameters = {
        # 'clf__hidden_layer_sizes': [(100), (100,100)]
        # 'vect__ngram_range': [(1,1), (1,2), (1,3), (1,4), (1,5)],
        # 'vect__binary': [True, False],
        # 'clf__C': [0.5, 1.0, 1.5, 2.0, 2.5, 3.0],
        # 'clf__kernel': ['linear', 'rbf', 'poly']
    }

    grid_search = GridSearchCV(pipeline, parameters, n_jobs=-1, verbose=1, cv=2, scoring='accuracy')
    grid_search.fit(data_inputs, data_outputs)

    return {
        "results": grid_search.cv_results_,
        "best_index": grid_search.best_index_,
        "best_params": grid_search.best_params_,
        "best_score": grid_search.best_score_
    }

def run(inputs=[]):
    results = {}
    summaries = {}
    for i in inputs:
        input_file = 'workdir/%s.json' % i
        data_file = 'workdir/%s-data.json' % i
        data = DataPreparator(InputTransformer(), validator, force_save=True).prepare(input_file, data_file)

        normal = runCase(data['input'], data['output'])

        random.Random(42).shuffle(data['output'])
        shuffled = runCase(data['input'], data['output'])

        results[i] = {
            'normal': normal,
            'shuffled': shuffled
        }
        
        summaries[i] = {
            'shuffled': {
                'best_score': shuffled['best_score'],
                'best_params': shuffled['best_params']
            },
            'normal': {
                'best_score': normal['best_score'],
                'best_params': normal['best_params']
            }
        }
        
    return (results, summaries)

if __name__ == '__main__':
    results_name = 'full-fold3'
    (r, s) = run(['socketio', 'd3', 'docker-ce', 'guava', 'jquery'])
    
    print('SUMMARY:')
    pprint(s)

    # with open('workdir/%s-summary.json' % results_name, 'w') as f:
    #     jsonData = pandas.Series(s).to_json()
    #     f.write(jsonData)
    # print('Saved summary')

    # with open('workdir/%s-details.json' % results_name, 'w') as f:
    #     jsonData = pandas.Series(r).to_json()
    #     f.write(jsonData)
    # print('Saved results')
    