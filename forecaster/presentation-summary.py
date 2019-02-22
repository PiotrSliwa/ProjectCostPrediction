import json
from pprint import pprint
import csv

def load(filename):
    with open(filename, encoding="utf8") as f:
        inputStr = f.read()
        return json.loads(inputStr)

def get_details(r):
    r['results']

def get_row(project, dataType, data):
    return {
        'project': project,
        'type': dataType,
        'best_score': data['best_score'],
        'C': data['best_params']['clf__C'],
        'binarization': 'Tak' if data['best_params']['vect__binary'] else 'Nie',
        'ngram_range': data['best_params']['vect__ngram_range']
    }

RESULT_NAME = 'full-fold3'

output = []
r = load('workdir/%s-summary.json' % RESULT_NAME)
with open('workdir/%s-summary.csv' % RESULT_NAME, 'w') as f:
    writer = csv.DictWriter(f, fieldnames=['project', 'type', 'best_score', 'C', 'binarization', 'ngram_range'])
    writer.writeheader()
    for (project, data) in r.items():
        writer.writerow(get_row(project, 'Losowe pary', data['shuffled']))
        writer.writerow(get_row(project, 'Dane poprawne', data['normal']))