import os
import requests

api_login = os.getenv('BUGZILLA_API_LOGIN')
api_key = os.getenv('BUGZILLA_API_TOKEN')

BASE_URL = 'https://bugzilla.mozilla.org'
URL = '{}/rest/bug'.format(BASE_URL)
creds = {'api_key': api_key}

web_ext_base = {
    'product': 'Toolkit',
    'component': [
        'WebExtensions: Android',
        'WebExtensions: Compatibility',
        'WebExtensions: Developer Tools',
        'WebExtensions: Extensions',
        'WebExtensions: Frontend',
        'WebExtensions: General',
        'WebExtensions: Request Handling',
        'WebExtensions: Untriaged'
    ],
    'status': ['UNCONFIRMED', 'NEW', 'ASSIGNED', 'REOPENED'],
}

def check_login():
    res = requests.get(
        '{}/rest/valid_login'.format(BASE_URL),
        params={
            'login': api_login,
            'api_key': api_key
        }
    )
    res.raise_for_status()


def get_bug(id):
    res = requests.get(URL + '/{}'.format(id))
    res.raise_for_status()
    return res.json()['bugs'][0]


def get_url(id):
    return BASE_URL + '/show_bug.cgi?id={}'.format(id)


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
    res = requests.put(url, params={'api_key': api_key}, json=data)
    res.raise_for_status()
