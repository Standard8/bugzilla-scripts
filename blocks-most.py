import os
import requests
from utils import check_login, get_url, URL, web_ext_base


def get_no_blockers():
    params = web_ext_base.copy()
    params.update({
        'f1': 'blocked',
        'o1': 'isnotempty'
    })
    res = requests.get(URL, params=params)
    res.raise_for_status()
    return res.json()['bugs']


if __name__=='__main__':
    check_login()
    blocks = {}
    for bug in get_no_blockers():
        if len(bug['blocks']) > 2:
            blocks[bug['id']] = len(bug['blocks'])

    sorted_list = sorted([(v, k) for k, v in blocks.items()])
    for count, bug_id in reversed(sorted_list):
        print '{} {}'.format(count, get_url(bug_id))
