import logging


class MockSlack:
    def __init__(self):
        self.messages = []
        self.logger = logging.getLogger("TESTING")
        self.logger.setLevel("DEBUG")
        self.logger.addHandler(logging.StreamHandler())

    def send(self, recipient, message):
        self.logger.info("SLACK SEND: {0}: {1}".format(recipient, message))
        msg = {"recipient": recipient, "message": message}
        if msg not in self.messages:
            self.messages.append(msg)
