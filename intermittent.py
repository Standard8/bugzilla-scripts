from datetime import datetime, date, timedelta
from urllib import urlencode

import requests
import sys

from utils import check_login, URL, creds

brasstacks_rest = 'https://brasstacks.mozilla.com/orangefactor/api/count/?'
brasstacks_info = ('https://brasstacks.mozilla.com/orangefactor/?'
                   'display=Bug&bugid={}&startday={}&endday={}&tree=all')


def fetch(product, component):
    bugs = []
    kw = {
        'product': product,
        'component': component,
        'short_desc': 'Intermittent',
        'status': ['UNCONFIRMED', 'ASSIGNED', 'REOPENED', 'NEW'],
    }

    res = requests.get(URL, params=kw)
    res.raise_for_status()
    bugs = res.json().get('bugs', [])
    print 'Found {} bugs.'.format(len(bugs))
    return bugs


def last_occurred(bug, days):
    print 'Bug: {}'.format(bug['id'])
    start = date.today() - timedelta(days=days)
    created = datetime.strptime(bug['creation_time'][:10], '%Y-%m-%d').date()
    # Assume the bug was created earlier than it was, just in case there
    # was any lag in creating the bug.
    lag = created - timedelta(days=10)
    if lag > start:
        print '  Ignoring because the bug is too new.'
        return False

    kw = {
        'bugid': bug['id'],
        'startday': start,
        'endday': date.today()
    }
    res = requests.get(brasstacks_rest, params=kw)
    res.raise_for_status()
    sorted_results = sorted([(k, v) for k, v in res.json()['oranges'].items()])

    for result in sorted_results:
        if result[1]['orangecount'] > 0:
            print '  This occurred on: {} '.format(result[0])
            return False

    print '  This has NOT occurred since: {}'.format(sorted_results[0][0])
    return True


def close(bug, days, dry_run):
    start = date.today() - timedelta(days=days)
    more_info = brasstacks_info.format(bug['id'], start, date.today())
    kw = {
      'ids': [bug['id']],
      'status': 'RESOLVED',
      'resolution': 'WORKSFORME',
      'comment': {
          'body': 'This intermittent has not occurred for '
                  'over {} days, so closing.\n\n{}'.format(days, more_info)
      }
    }
    url = URL + '/%s' % bug['id']
    if not dry_run:
        print '  Closing on bugzilla.'
        res = requests.put(url, params=creds, json=kw)
        res.raise_for_status()


if __name__ == '__main__':
    product = sys.argv[1]
    component = sys.argv[2]
    days = int(sys.argv[3])
    dry_run = '--dry-run' in sys.argv

    print ('Product: {}, component: {}, days since: {}'
           .format(product, component, days))
    if dry_run:
        print 'This is a dry run, won\'t actually close any bugs.'

    closed = 0
    assert days > 30, 'Probably best to test for more than 30 days.'
    check_login()
    bugs = fetch(product, component)
    for bug in bugs:
        should_close = last_occurred(bug, days)
        if should_close:
            closed += 1
            close(bug, days, dry_run)

    print 'Found: {} bugs'.format(len(bugs))
    print 'Closed: {} bugs'.format(closed)
    print 'Complete.'
