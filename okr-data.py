from datetime import datetime, timedelta
import requests

from utils import URL


def fetch():
    bugs = []
    kw = {
        'o1': 'equals',
        'v1': '+',
        'f1': 'cf_blocking_webextensions'
    }

    res = requests.get(URL, params=kw)
    res.raise_for_status()
    bugs = res.json().get('bugs', [])
    return bugs

if __name__ == '__main__':
    start = datetime.strptime('2017-03-27', '%Y-%m-%d').date()
    result = {}
    total = 0
    for k in range(0, (datetime.today().date() - start).days, 7):
        result[(start + timedelta(days=k))] = []

    bugs = fetch()
    for bug in bugs:
        if not bug['cf_last_resolved']:
            continue

        total += 1
        resolved = datetime.strptime(bug['cf_last_resolved'][:10], '%Y-%m-%d').date()
        if resolved < start:
            continue

        beginning_of_week = resolved - timedelta(days=resolved.weekday())
        result[beginning_of_week].append(bug)

    cumulative = 0
    for k in sorted(result.keys()):
        number_bugs = len(result[k])
        cumulative += number_bugs
        print ','.join((str(k), str(number_bugs), str(total), str(cumulative)))
