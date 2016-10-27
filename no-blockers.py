import os
import requests
import time
from utils import check_login, get_bug, get_url, URL, web_ext_base


def get_no_blockers():
    params = web_ext_base.copy()
    params.update({
        'f1': 'dependson',
        'o1': 'isnotempty'
    })
    res = requests.get(URL, params=params)
    res.raise_for_status()
    return res.json()['bugs']


if __name__=='__main__':
    for bug in get_no_blockers():
        open_dependents = 0
        for dependent_id in bug['depends_on']:
            dependent = get_bug(dependent_id)
            if dependent['status'] != 'RESOLVED':
                open_dependents += 1

        if not open_dependents:
            print '{}, {}'.format(bug['summary'], get_url(bug['id']))

        # Hack to stop Bugzilla banning me.
        time.sleep(30)
