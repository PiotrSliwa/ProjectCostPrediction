import json
from pprint import pprint
import csv

def load(filename):
    with open(filename, encoding="utf8") as f:
        inputStr = f.read()
        return json.loads(inputStr)

def get_details(r):
    r['results']

def get_rows(project, dataType, data):
    result = []
    for i in range(0, len(data['params'])):
        result.append({
            'project': project,
            'type': dataType,
            'mean_test_score': data['mean_test_score'][i],
            'std_test_score': data['std_test_score'][i],
            'C': data['params'][i]['clf__C'],
            'binarization': 'Tak' if data['params'][i]['vect__binary'] else 'Nie',
            'ngram_range': data['params'][i]['vect__ngram_range']
        })
    return result

RESULT_NAME = 'full-fold3'

output = []
r = load('workdir/%s-details.json' % RESULT_NAME)
with open('workdir/%s-results.csv' % RESULT_NAME, 'w') as f:
    writer = csv.DictWriter(f, fieldnames=['project', 'type', 'mean_test_score', 'std_test_score', 'C', 'binarization', 'ngram_range'])
    writer.writeheader()
    for (project, data) in r.items():
        writer.writerows(get_rows(project, 'Losowe pary', data['shuffled']['results']))
        writer.writerows(get_rows(project, 'Dane poprawne', data['normal']['results']))