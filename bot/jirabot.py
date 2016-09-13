import logging
from collections import deque

from bot.message_to_jira_attachment_converter import MessageToJiraAttachmentConverter
from bot.warning_detector import JiraWarningDetector


class JiraBot:
    def __init__(self, jira, slack, project, label, channel, wip_limit=5, logger=None):
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger("TESTING")
            self.logger.setLevel("DEBUG")
            self.logger.addHandler(logging.StreamHandler())

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

        self.project = project
        self.label = label
        self.wip_limit = wip_limit
        self.jira = jira.with_project(self.project).with_label(self.label)

        self.warning_detector = JiraWarningDetector(self.jira, project, label, self.logger, wip_limit)
        self.jira_id_to_attachment_converter = MessageToJiraAttachmentConverter(self.jira)

    def process_messages(self):
        my_id = self.bot_id.lower()
        messages = self.slack.read_next_messages_for_channel(self.channel_id)
        messages = filter(lambda m: "text" in m, messages)
        for message in messages:
            text = message["text"].lower()
            user = message.get("user") or ""
            self.logger.debug("Processing message: {0}".format(text))
            if my_id in text:
                self.logger.debug("I was mentioned")
                self.process_message_to_me(text, user)

    def process_message_to_me(self, text, user):
        messages = []

        if "show" in text:
            if "warnings" in text or "errors" in text:
                self.logger.debug("Received command to show warnings")
                messages += self.get_warnings()
            if "new issues" in text or "new cards" in text or "new tickets" in text or "new jiras" in text:
                self.logger.debug("Received command to show new issues")
                messages.append(self.get_new_issues_summary())
            if "in progress" in text:
                self.logger.debug("Received command to show in progress issues")
                messages.append(self.get_in_progress_issues())
            if "to do" in text:
                self.logger.debug("Received command to show to do list")
                messages.append(self.get_to_do_issues())
            self.logger.debug("Finished processing show command")

        if len(messages) > 0:
            for message in messages:
                self.send(self.channel, message, force=True)
        else:
            self.send(self.channel, "Not sure what you mean by that <@{0}>, here's what I can do".format(user),
                      force=True, attachments=[self.get_help_attachment()])

    def get_help_attachment(self):
        return {
            "fallback": "I can do all sorts!",
            "pretext": "",
            "title": "I can do all sorts!",
            "title_link": "",
            "text": "Ask me to:\n" +
                    ":one: 'show warnings'\n" +
                    ":two: 'show to do'\n" +
                    ":three: 'show in progress'\n" +
                    "and always remember to mention me by name!"
        }

    def send_periodic_update(self):
        messages = self.get_warnings()
        messages += self.get_new_issues_on_backlog()
        for message in messages:
            self.send(self.channel, message, force=False)

    def get_warnings(self):
        warnings = self.warning_detector.find_warnings()

        if len(warnings) == 0:
            return [
                "There are no warnings. It's all good!",
                ":partyparrot:"
            ]
        else:
            return warnings

    def send(self, recipient, message, force, attachments=None):
        msg = {"recipient": recipient, "message": message}
        if msg not in self.history or force:
            attachments = attachments or []
            attachments += self.jira_id_to_attachment_converter.apply(message)
            self.history.append(msg)
            self.slack.send(recipient, message, attachments)

    def get_new_issues_on_backlog(self):
        issues = self.jira.status_is_not(["in progress", "done", "closed"]).created_in_last_n_days(1).get_issues()
        for issue in issues:
            message = ':memo: New issue {0} added'.format(issue)
            yield message

    def get_new_issues_summary(self):
        issues = self.jira.status_is_not(["in progress", "done", "closed"]).created_in_last_n_days(1).get_issues()
        ids = map(lambda i: "{0}".format(i), issues)
        if len(ids):
            message = ':memo: The following *new issues* issues have been added in the last 24 hours: {0}'.format(
                ', '.join(ids))
        else:
            message = ':memo: No issues added in the last 24 hours'
        return message

    def get_in_progress_issues(self):
        issues = self.jira.status_is("in progress").get_issues()
        ids = map(lambda i: "{0}".format(i), issues)
        if len(ids) > 0:
            message = ':memo: The following issues are currently *in progress*: {0}'.format(', '.join(ids))
        else:
            message = ':memo: Nothing currently marked as in progress!'
        return message

    def get_to_do_issues(self):
        issues = self.jira.status_is("to do").get_issues()
        ids = map(lambda i: "{0}".format(i), issues)
        if len(ids) > 0:
            message = ':memo: The following issues are currently on the *to do list*: {0}'.format(', '.join(ids))
        else:
            message = ':memo: The To Do list is empty!'
        return message
