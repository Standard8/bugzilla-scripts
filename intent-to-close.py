import os
import requests
from utils import check_login, creds, URL

product = os.getenv('BUGZILLA_PRODUCT')
component = os.getenv('BUGZILLA_COMPONENT)


def get_marked_addons():
    params = {
        'product': product,
        'component': component,
        'status': ['UNCONFIRMED', 'NEW', 'ASSIGNED', 'REOPENED'],
        'order': 'Bug Number',
        'f1': 'status_whiteboard',
        'o1': 'substring',
        'v1': '[intent-to-close]'
    }
    return requests.get(URL, params=params).json()['bugs']


def actually_close(bug):
    data = {
        'ids': [bug],
        'status': 'RESOLVED',
        'resolution': 'WONTFIX'
    }
    url = URL + '/%s' % bug['id']
    res = requests.put(url, params=creds, json=data)
    res.raise_for_status()


if __name__=='__main__':
    check_login()
    bugs = get_marked_addons()
    for bug in bugs:
        print 'Actually closing bug:', bug['id']
        actually_close(bug)
