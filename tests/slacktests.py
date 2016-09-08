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

    def test_get_history_for_channel(self):
        # slacker = Slacker('xoxb-68771251987-j7q9lApp7dlsI3kWDz49FFgR')
        # response = slacker.channels.list()
        # for c in response.body['channels']:
        #    print '{0} {1}'.format(c['name'], c['id'])
        response = self.slack.api_call(
            "channels.history",
            channel="C02C5758Z",
            username='@jirabot'
        )
        for x in response['messages']:
            print x['text']

    def test_read_some_messages(self):
        if self.slack.rtm_connect():
            while True:
                msgs = self.slack.rtm_read()
                for m in msgs:
                    print m
                time.sleep(1)

    def test_sending_a_message(self):
        print self.slack.api_call(
            "chat.postMessage",
            channel="dan_test",
            text="Hello from Python! :tada:",
            username='@jirabot',
            icon_emoji=':office:'
        )

    def test_join_a_channel(self):
        channels_call = self.slack.api_call("channels.list")
        if channels_call.get("ok"):
            channels = channels_call.get('channels')
            for c in channels:
                print c
            print filter(lambda c: c.get("name") == "dan_test", channels)

            # print self.slack.api_call("channels.join", name="dan_test")

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
