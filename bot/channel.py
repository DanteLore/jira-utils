from collections import deque


class Channel:
    def __init__(self, slack, channel, jira_id_to_attachment_converter, logger):
        self.jira_id_to_attachment_converter = jira_id_to_attachment_converter
        self.logger = logger
        self.history = deque(maxlen=40)
        self.slack = slack
        self.channel = channel
        self.channel_id = slack.get_channel_id(channel)
        if self.channel_id:
            self.logger.info("Operating on channel '{0}' (id:'{1}')".format(self.channel, self.channel_id))
        else:
            raise ValueError("Could not find a channel or group named {0}".format(channel))

        self.bot_id = slack.get_user_id("JiraBot")
        if self.bot_id:
            self.logger.info("My name is JiraBot and my id is '{0}')".format(self.bot_id))
        else:
            raise ValueError("Can't look up bot id for 'JiraBot'")

    def send(self, message, force, attachments=None):
        if message not in self.history or force:
            attachments = attachments or []
            attachments += self.jira_id_to_attachment_converter.apply(message)
            self.history.append(message)
            self.slack.send(self.channel, message, attachments)

    def get_messages(self):
        my_id = self.bot_id.lower()
        messages = self.slack.read_next_messages_for_channel(self.channel_id)
        messages = filter(lambda m: "text" in m, messages)
        for message in messages:
            text = message["text"].lower()
            user = message.get("user") or ""
            self.logger.debug(u"Processing message: {0}".format(text))
            if my_id in text:
                self.logger.debug("I was mentioned")
                yield text, user