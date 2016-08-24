import time
import unittest

from slackclient import SlackClient

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

        #print self.slack.api_call("channels.join", name="dan_test")