import time
import unittest

import unicodedata
from fuzzywuzzy import process
from slackclient import SlackClient
from slacker import Slacker

BOT_NAME = 'jirabot'


# Get tokens from: https://api.slack.com/web#authentication
# Bot ID: U20NP7DV1


class SlackTests(unittest.TestCase):
    def setUp(self):
        self.slack = SlackClient('??')

    def test_connect(self):
        api_call = self.slack.api_call("users.list")
        if api_call.get('ok'):
            # retrieve all users so we can find our bot
            users = api_call.get('members')
            for user in users:
                if 'name' in user and user.get('name') == BOT_NAME:
                    print("Bot ID for '" + user['name'] + "' is " + user.get('id'))
        else:
            print("could not find bot user with the name " + BOT_NAME)

    def test_read_some_messages(self):
        if self.slack.rtm_connect():
            print "connected"
            while True:
                msgs = self.slack.rtm_read()
                for m in msgs:
                    print m
                time.sleep(0.1)

    def test_sending_a_message(self):
        print self.slack.api_call(
            "chat.postMessage",
            channel="dan_test",
            text="Hello from Python! <@U1LSJ8JGY> :tada:\nI'm awesome!",
            username='@jirabot',
            icon_emoji=':office:'
        )

    def test_list_channels(self):
        groups = self.slack.api_call("groups.list").get('groups')
        channels = groups + self.slack.api_call("channels.list").get('channels')
        for c in channels:
            print c
        print filter(lambda c: c.get("name") == "dan_test", channels)[0]["id"]

    def test_list_users(self):
        users = self.slack.api_call("users.list")
        print users
        users = users.get('members')
        for u in users:
            print u
        print filter(lambda c: c.get("name") == "jirabot", users)[0]["id"]

    def test_sending_an_attachment_message(self):
        print self.slack.api_call(
            "chat.postMessage",
            channel="dan_test",
            username='@jirabot',
            icon_emoji=':memo:',
            attachments=[
                {
                    "fallback": "New ticket from Andrea Lee - Ticket #1943: Can't rest my password - https://groove.hq/path/to/ticket/1943",
                    "pretext": "New Jira added",
                    "title": "XXX-123: Can't reset my password",
                    "title_link": "https://logicalgenetics.com",
                    "text": "This is the description of the issue about the changing password thing <@U20NP7DV1>",
                    "color": "#7CD197"
                }
            ]
        )

    def test_name_matching(self):
        users = self.slack.api_call("users.list")
        users = users.get('members')

        users = ({
                     "fullname": unicodedata.normalize('NFKD', u.get("real_name") or u"").encode('ascii', 'ignore'),
                     "id": u.get("id") or "",
                     "name": u.get("name") or ""
                 } for u in users)

        users = [u for u in users if u["fullname"] and u["id"] and u["name"]]

        cutoff = 80

        name, _ = process.extractOne("Dan Taylor", users, score_cutoff=cutoff)
        self.assertEqual("dan_taylor", name.get("name"))

        name, _ = process.extractOne("Cody.Barzey-Francois", users, score_cutoff=cutoff)
        self.assertEqual("tachyon", name.get("name"))

        name, _ = process.extractOne("Anthony Blanchflower", users, score_cutoff=cutoff)
        self.assertEqual("tonyblanch", name.get("name"))

        name, _ = process.extractOne("Bhavana Bhosale", users, score_cutoff=cutoff)
        self.assertEqual("bhavanab", name.get("name"))

        name, _ = process.extractOne("Amarnath.Kallam", users, score_cutoff=cutoff)
        self.assertEqual("amarnath.kallam", name.get("name"))
