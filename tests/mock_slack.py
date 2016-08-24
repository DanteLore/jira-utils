class MockSlack:
    def __init__(self):
        self.messages = []

    def send(self, recipient, message):
        print "{0}: {1}".format(recipient, message)
        self.messages.append({"recipient": recipient, "message": message})