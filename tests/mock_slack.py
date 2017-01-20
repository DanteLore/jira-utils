class MockSlack:
    def __init__(self, incoming_messages=None, name_lookup=None):
        self.incoming_messages = incoming_messages or []
        self.outgoing_messages = []
        self.uploaded_files = []
        self.name_lookup = name_lookup or {}

    def read_next_messages_for_channel(self, channel_id):
        return self.incoming_messages

    def add_incoming(self, message):
        self.incoming_messages.append(message)

    def get_channel_id(self, channel):
        return "CHANNEL_1"

    def get_user_id(self, name):
        return "BOTID"

    def search_user_id(self, name):
        return self.name_lookup.get(name)

    def send(self, recipient, message, attachments):
        msg = {"recipient": recipient, "message": message}
        self.outgoing_messages.append(msg)

    def upload_file(self, channel, filename, file_handle):
        self.uploaded_files.append(filename)
