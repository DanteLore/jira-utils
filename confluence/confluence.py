import getpass
import json
import logging

import keyring
import requests


class Confluence:
    def __init__(self, base_url, username, logger=None):
        self.base_url = base_url
        self.auth = self.get_login(username)
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger("TESTING")
            self.logger.setLevel("DEBUG")
            self.logger.addHandler(logging.StreamHandler())

    def get_page_ancestors(self, page_id):
        url = '{0}/{1}?expand=ancestors'.format(self.base_url, page_id)
        r = requests.get(url, auth=self.auth)
        r.raise_for_status()
        return r.json()['ancestors']

    def get_page_body(self, page_id):
        url = '{0}/{1}?expand=body.storage'.format(self.base_url, page_id)
        r = requests.get(url, auth=self.auth)
        r.raise_for_status()
        return r.json()['body']['storage']['value']

    def get_page_info(self, page_id):
        url = '{0}/{1}'.format(self.base_url, page_id)
        r = requests.get(url, auth=self.auth)
        r.raise_for_status()
        return r.json()

    def get_login(self, username):
        password = keyring.get_password('confluence_script', username)

        if password is None:
            self.logger.info("Saved password for user {0}".format(username))
            password = getpass.getpass()
            keyring.set_password('confluence_script', username, password)

        return username, password

    def put_page(self, url, data):
        r = requests.put(url, data=data, auth=self.auth, headers={'Content-Type': 'application/json'})
        r.raise_for_status()

    def post_page(self, url, data):
        r = requests.post(self.base_url, data=data, auth=self.auth, headers={'Content-Type': 'application/json'})
        r.raise_for_status()

    def update_page(self, page_id, html, title=None):
        info = self.get_page_info(page_id)

        ver = int(info['version']['number']) + 1

        ancestors = self.get_page_ancestors(page_id)
        anc = ancestors[-1]
        del anc['_links']
        del anc['_expandable']
        del anc['extensions']

        if title:
            info['title'] = title

        data = {
            'id': str(page_id),
            'type': 'page',
            'title': info['title'],
            'version': {'number': ver},
            'ancestors': [anc],
            'body': {
                'storage':
                    {
                        'representation': 'storage',
                        'value': str(html),
                    }
            }
        }

        data = json.dumps(data)
        url = '{0}/{1}'.format(self.base_url, page_id)
        self.put_page(url, data)
        self.logger.info("Updated page at '{0}' to version {1}".format(info['title'], ver))

    def create_page(self, parent_id, title, html):
        data = {
            'type': 'page',
            'title': title,
            'ancestors': [{'id': parent_id}],
            'space': {'key': 'BI'},
            'body': {
                'storage':
                    {
                        'representation': 'storage',
                        'value': str(html),
                    }
            }
        }
        data = json.dumps(data)

        self.post_page(self.base_url, data)
        self.logger.info("Created page at '{0}'".format(title))
