from slackclient import SlackClient


class Slack:
    def __init__(self, key):
        self.slack = SlackClient(key)

    def send(self, recipient, message):
        print "{0}: {1}".format(recipient, message)
        print self.slack.api_call(
            "chat.postMessage",
            channel="dan_test",
            text="*{0}*: {1}".format(recipient, message),
            username='@jirabot',
            icon_emoji=':office:'
        )