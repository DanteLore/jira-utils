import logging


class MockSlack:
    def __init__(self, incoming_messages=None):
        self.incoming_messages = incoming_messages or []
        self.outgoing_messages = []
        self.logger = logging.getLogger("TESTING")
        self.logger.setLevel("DEBUG")
        self.logger.addHandler(logging.StreamHandler())

    def read_next_messages_for_channel(self, channel_id):
        return self.incoming_messages

    def add_incoming(self, message):
        self.incoming_messages.append(message)

    def get_channel_id(self, channel):
        return "CHANNEL_1"

    def get_user_id(self, name):
        return "BOTID"

    def send(self, recipient, message):
        self.logger.info("SLACK SEND: {0}: {1}".format(recipient, message))
        msg = {"recipient": recipient, "message": message}
        self.outgoing_messages.append(msg)
