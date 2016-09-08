import logging
from slackclient import SlackClient
from collections import deque


class Slack:
    def __init__(self, key, attachment_converter, logger=None):
        self.attachment_converter = attachment_converter

        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger("TESTING")
            self.logger.setLevel("DEBUG")
            self.logger.addHandler(logging.StreamHandler())

        self.slack = SlackClient(key)
        self.history = deque(maxlen=40)

    def send(self, recipient, message):
        msg = {"recipient": recipient, "message": message}

        if msg not in self.history:
            self.history.append(msg)
            self.logger.info("SLACK SEND: {0}: {1}".format(recipient, message))

            self.slack.api_call(
                "chat.postMessage",
                channel=recipient,
                text=message,
                username='@jirabot',
                icon_emoji=':office:',
                attachments=self.attachment_converter.apply(message)
            )
