import argparse
import logging
import re
from itertools import groupby
from time import sleep

from bot.slack import Slack
from jira_utils.jira_utils import Jira


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

        self.slack = slack
        self.project = project
        self.label = label
        self.wip_limit = wip_limit
        self.channel = channel

        self.jira = jira.with_project(self.project).with_label(self.label)

    def process(self):
        self.assigned_but_not_in_progress()
        self.too_many_in_progress()
        self.notify_new_issues_on_backlog()
        self.in_progress_but_not_assigned()

    def notify_new_issues_on_backlog(self):
        issues = self.jira.status_is_not(["in progress", "done", "closed"]).created_in_last_n_days(1).get_issues()
        for issue in issues:
            message = ':memo: New issue {0} added'.format(issue)
            self.slack.send(self.channel, message)

    def too_many_in_progress(self):
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
                self.slack.send(self.channel, msg)

    def assigned_but_not_in_progress(self):
        issues = self.jira \
            .status_is_not(["in progress", "done", "closed"]) \
            .assigned() \
            .get_issues()
        for issue in issues:
            assignee = issue.fields.assignee
            message = ':warning: {0} is assigned to *{1}* but still in the {2} state'.format(issue,
                                                                                             assignee,
                                                                                             issue.fields.status)
            self.slack.send(self.channel, message)

    def in_progress_but_not_assigned(self):
        issues = self.jira \
            .status_is("in progress") \
            .not_assigned() \
            .get_issues()
        for issue in issues:
            message = ':warning: {0} is marked as In Progress but not assigned to anyone'.format(issue)
            self.slack.send(self.channel, message)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Jira Bot')
    parser.add_argument('--jira', help='Jira Server', required=True)
    parser.add_argument('--project', help='Jira Project ID', required=True)
    parser.add_argument('--label', help='Jira Label', required=True)
    parser.add_argument('--wip-limit', help='How many In Progress issues is too many?', default="3")
    parser.add_argument('--slack-key', help='The key for slack', required=True)
    parser.add_argument('--channel', help='The channel on which to complain about stuff', required=True)
    parser.add_argument('--forever', help='Use this switch to run the script forever (once ever 5 mins)',
                        action='store_true', default=False)
    parser.add_argument('--log-level', help='Log level to use. Default=INFO', default="INFO")

    args = parser.parse_args()

    logger = logging.getLogger("JiraBot")
    logger.setLevel(args.log_level)
    logger.addHandler(logging.StreamHandler())

    jira = Jira(args.jira)
    attachment_converter = MessageToJiraAttachmentConverter(jira)
    slack = Slack(args.slack_key, attachment_converter, logger)

    bot = JiraBot(jira=jira,
                  slack=slack,
                  project=args.project,
                  label=args.label,
                  channel=args.channel,
                  logger=logger,
                  wip_limit=args.wip_limit)

    while True:
        try:
            logger.info("Processing loop started")
            bot.process()
            logger.info("Processing loop finished")
        except Exception as e:
            logger.error(e.message)
            slack.send("dan_taylor", "I crashed!!")
            slack.send("dan_taylor", e.message)
        if not args.forever:
            break
        sleep(300)
