import logging

from slackclient import SlackClient


class Slack:
    def __init__(self, key, logger=None):
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger("TESTING")
            self.logger.setLevel("DEBUG")
            self.logger.addHandler(logging.StreamHandler())

        self.slack = SlackClient(key)
        if self.slack.rtm_connect():
            self.logger.info("Connected real time web socket to slack")
        else:
            raise IOError("Failed to connect real time web socket to slack. Check the key you specified is correct!")

    def read_next_messages_for_channel(self, channel_id):
        while True:
            msgs = self.slack.rtm_read()
            channel_msgs = [x for x in msgs if "channel" in x and x["channel"] == channel_id]
            if len(msgs) > 0:
                self.logger.debug("Read {0} total messages from slack {1} for channel {2}"
                                  .format(len(msgs), len(channel_msgs), channel_id))
            return channel_msgs

    def all_channels(self):
        groups = self.slack.api_call("groups.list").get('groups')
        channels = groups + self.slack.api_call("channels.list").get('channels')
        return channels

    def all_users(self):
        users = self.slack.api_call("users.list").get('members')
        return users

    def get_channel_id(self, channel):
        chan = next((c for c in self.all_channels() if c["name"].lower() == channel.lower()), None)
        if chan:
            return chan["id"]
        else:
            return None

    def get_user_id(self, name):
        user = next((u for u in self.all_users() if u["name"].lower() == name.lower()), None)
        if user:
            return user["id"]
        else:
            return None

    def send(self, recipient, message, attachments=None):
        self.logger.info("SLACK SEND: {0}: {1}".format(recipient, message))

        self.slack.api_call(
            "chat.postMessage",
            channel=recipient,
            text=message,
            username='@jirabot',
            icon_emoji=':office:',
            attachments=attachments or []
        )
