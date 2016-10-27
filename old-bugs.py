import datetime
import os
import requests
from utils import creds, intent_to_close, URL

product = os.getenv('BUGZILLA_PRODUCT')
component = os.getenv('BUGZILLA_COMPONENT)


def get_old_addons():
    params = {
        'product': product,
        'component': component,
        'status': ['UNCONFIRMED', 'NEW', 'ASSIGNED', 'REOPENED'],
        'order': 'Bug Number',
        'f1': 'bug_id',
        'v1': '500000',
        'o1': 'lessthan'
    }
    return requests.get(URL, params=params).json()['bugs']


def intent_to_close(bug, age):
    data = {
        'ids': [bug],
        'whiteboard': bug['whiteboard'] + '[intent-to-close]',
        'comment': {
            'body': 'Due to a long period of inactivity on this bug (%2.2f years), '
                    'I am intending to close this bug within a month or so in '
                    'accordance with: '
                    'https://wiki.mozilla.org/Add-ons/OldBugs '
                    'Please remove [intent-to-close] from the whiteboard and '
                    'comment on this bug if you would like to keep it open.' %
                    age
        }
    }
    url = bugzilla + '/%s' % bug['id']
    res = requests.put(url, params=creds, json=data)
    res.raise_for_status()


def should_close(bug):
    last_change = datetime.datetime.strptime(
        bug['last_change_time'], '%Y-%m-%dT%H:%M:%SZ')
    age = datetime.datetime.today() - last_change
    age = age.days / 365.0
    if '[intent-to-close]' in bug['whiteboard']:
        return False, age
    return age > max_age, age



if __name__=='__main__':
    check_login()
    bugs = get_old_addons()
    for bug in bugs:
        close, age = should_close(bug)
        if close:
            print 'Intent to close:', bug['id']
            intent_to_close(bug, age)
        else:
            print 'Not closing:', bug['id'], 'only', age, 'years old.'
