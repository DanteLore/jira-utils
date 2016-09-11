import logging
import re
from collections import deque
from itertools import groupby
from threading import Thread


class MessageToJiraAttachmentConverter:
    def __init__(self, jira):
        self.jira = jira
        self.format_str = "{0}/browse/{{0}}".format(jira.server.rstrip('/'))
        self.pattern = re.compile("([A-Z]+-[0-9]+)")

    def get_attachments(self, message):
        for id in self.pattern.findall(message):
            issue = self.jira.with_id(id).get_issues()[0]

            yield {
                "fallback": "{0}: {1}".format(id, issue.fields.summary),
                "pretext": "",
                "title": "{0}: {1}".format(id, issue.fields.summary),
                "title_link": self.format_str.format(id),
                "text": ""
            }

    def apply(self, message):
        return list(self.get_attachments(message))


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

    def process_messages(self):
        my_id = self.bot_id.lower()
        messages = self.slack.read_next_messages_for_channel(self.channel_id)
        messages = filter(lambda m: "text" in m, messages)
        messages = map(lambda m: m["text"].lower(), messages)
        for msg in messages:
            self.logger.debug("Processing message: {0}".format(msg))
            if my_id in msg:
                self.logger.debug("I was mentioned")
                self.process_message_to_me(msg)

    def process_message_to_me(self, msg):
        if "show" in msg:
            if "warnings" in msg or "errors" in msg:
                self.logger.debug("Received command to show warnings")
                self.send_warnings(force=True)
            if "new issues" in msg or "new cards" in msg or "new tickets" in msg or "new jiras" in msg:
                self.logger.debug("Received command to show new issues")
                self.notify_new_issues_summary(force=True)
            if "in progress" in msg:
                self.logger.debug("Received command to show in progress issues")
                self.notify_in_progress_issues(force=True)
            if "to do" in msg:
                self.logger.debug("Received command to show to do list")
                self.notify_to_do_issues(force=True)
            self.logger.debug("Finished processing show command")

    def send_periodic_update(self):
        self.send_warnings(force=False)
        self.notify_new_issues_on_backlog(force=False)

    def send_warnings(self, force=False):
        self.assigned_but_not_in_progress(force)
        self.too_many_in_progress(force)
        self.in_progress_but_not_assigned(force)

    def send(self, recipient, message, force):
        msg = {"recipient": recipient, "message": message}
        if msg not in self.history or force:
            self.history.append(msg)
            self.slack.send(recipient, message)

    def notify_new_issues_on_backlog(self, force):
        issues = self.jira.status_is_not(["in progress", "done", "closed"]).created_in_last_n_days(1).get_issues()
        for issue in issues:
            message = ':memo: New issue {0} added'.format(issue)
            self.send(self.channel, message, force)

    def notify_new_issues_summary(self, force):
        issues = self.jira.status_is_not(["in progress", "done", "closed"]).created_in_last_n_days(1).get_issues()
        ids = map(lambda i: "{0}".format(i), issues)
        if len(ids):
            message = ':memo: The following *new issues* issues have been added in the last 24 hours: {0}'.format(', '.join(ids))
        else:
            message = ':memo: No issues added in the last 24 hours'
        self.send(self.channel, message, force)

    def notify_in_progress_issues(self, force):
        issues = self.jira.status_is("in progress").get_issues()
        ids = map(lambda i: "{0}".format(i), issues)
        if len(ids) > 0:
            message = ':memo: The following issues are currently *in progress*: {0}'.format(', '.join(ids))
        else:
            message = ':memo: Nothing currently marked as in progress!'
        self.send(self.channel, message, force)

    def notify_to_do_issues(self, force):
        issues = self.jira.status_is("to do").get_issues()
        ids = map(lambda i: "{0}".format(i), issues)
        if len(ids) > 0:
            message = ':memo: The following issues are currently on the *to do list*: {0}'.format(', '.join(ids))
        else:
            message = ':memo: The To Do list is empty!'
        self.send(self.channel, message, force)

    def too_many_in_progress(self, force):
        issues = self.jira.status_is("In Progress").assigned().get_issues()
        for k, v in groupby(issues, lambda i: i.fields.assignee):
            ids = map(lambda x: "{0}".format(x), list(v))
            self.logger.debug("{0} {1}".format(k, len(ids)))
            if len(ids) >= self.wip_limit:
                msg = ":warning: *{0}* currently has {1} jira issues in progress. That's too many. Here's a list: {2}".format(
                    k,
                    len(ids),
                    ", ".join(ids)
                )
                self.send(self.channel, msg, force)

    def assigned_but_not_in_progress(self, force):
        issues = self.jira \
            .status_is_not(["in progress", "done", "closed"]) \
            .assigned() \
            .get_issues()
        for issue in issues:
            assignee = issue.fields.assignee
            message = ':warning: {0} is assigned to *{1}* but still in the {2} state'.format(issue,
                                                                                             assignee,
                                                                                             issue.fields.status)
            self.send(self.channel, message, force)

    def in_progress_but_not_assigned(self, force):
        issues = self.jira \
            .status_is("in progress") \
            .not_assigned() \
            .get_issues()
        for issue in issues:
            message = ':warning: {0} is marked as In Progress but not assigned to anyone'.format(issue)
            self.send(self.channel, message, force)
