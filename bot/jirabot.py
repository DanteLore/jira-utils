import logging

from bot.channel import Channel
from bot.jira_query_executor import JiraQueryExecutor
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

        jira = jira.with_project(project).with_label(label)
        self.warning_detector = JiraWarningDetector(jira, project, label, self.logger, wip_limit)
        self.jira_executor = JiraQueryExecutor(jira)
        self.channel = Channel(slack, channel, MessageToJiraAttachmentConverter(jira), self.logger)

    def process_messages(self):
        for text, user in self.channel.get_messages():
            self.process_message_to_me(text, user)

    def process_message_to_me(self, text, user):
        messages = []

        if "show" in text:
            if "warnings" in text or "errors" in text:
                self.logger.debug("Received command to show warnings")
                messages += self.get_warnings()
            if "new issues" in text or "new cards" in text or "new tickets" in text or "new jiras" in text:
                self.logger.debug("Received command to show new issues")
                messages.append(self.jira_executor.get_new_issues_summary())
            if "in progress" in text:
                self.logger.debug("Received command to show in progress issues")
                messages.append(self.jira_executor.get_in_progress_issues())
            if "to do" in text:
                self.logger.debug("Received command to show to do list")
                messages.append(self.jira_executor.get_to_do_issues())
            if "backlog" in text:
                self.logger.debug("Received command to show backlog")
                messages.append(self.jira_executor.get_backlog_issues())
            self.logger.debug("Finished processing show command")

        if "status" in text:
            if "summary" in text:
                self.logger.debug("Received command to provide a status summary")
                messages.append(self.jira_executor.get_status_summary())
            self.logger.debug("Finished processing status command")

        if len(messages) > 0:
            for message in messages:
                self.channel.send(message, force=True)
        else:
            self.channel.send("Not sure what you mean by that <@{0}>, here's what I can do".format(user),
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
                    ":four: 'show backlog'\n" +
                    ":five: 'status summary'\n" +
                    "and always remember to mention me by name!"
        }

    def send_periodic_update(self):
        messages = self.get_warnings()
        messages += self.jira_executor.get_new_issues_on_backlog()
        for message in messages:
            self.channel.send(message, force=False)

    def get_warnings(self):
        warnings = self.warning_detector.find_warnings()

        if len(warnings) == 0:
            return [
                "There are no warnings. It's all good!",
                ":partyparrot:"
            ]
        else:
            return warnings


