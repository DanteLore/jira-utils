import time
import unittest

from slackclient import SlackClient
from slacker import Slacker

BOT_NAME = 'jirabot'


# Get tokens from: https://api.slack.com/web#authentication
# Bot ID: U20NP7DV1


class SlackTests(unittest.TestCase):
    def setUp(self):
        self.slack = SlackClient('???')

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
                    "text": "This is the description of the issue about the changing password thing",
                    "color": "#7CD197"
                }
            ]
        )
