import argparse
from itertools import groupby
from bot.slack import Slack
from jira_utils.jira_utils import Jira


class JiraBot:
    def __init__(self, jira, slack, project, label, wip_limit = 5):
        self.slack = slack
        self.project = project
        self.label = label
        self.wip_limit = wip_limit

        self.jira = jira.with_project(self.project).with_label(self.label)

    def start(self):
        self.assigned_but_not_in_progress()
        self.too_many_in_progress()

    def too_many_in_progress(self):
        issues = self.jira.status_is("In Progress").assigned().get_issues()
        for k, v in groupby(issues, lambda i: i.fields.assignee):
            ids = map(lambda x: "{0}".format(x), list(v))
            print "{0} {1}".format(k, len(ids))
            if len(ids) >= self.wip_limit:
                msg = "Warning: You currently have {0} jira issues in progress. That's too many. Here's a list: {1}".format(
                    len(ids),
                    ", ".join(ids)
                )
                self.slack.send(k, msg)

    def assigned_but_not_in_progress(self):
        issues = self.jira\
            .status_is_not(["in progress", "done", "closed"])\
            .assigned()\
            .get_issues()
        for issue in issues:
            recipient = issue.fields.assignee
            message = 'Warning: {0} "{1}" is assigned to you but still in the {2} state'.format(issue,
                                                                                                issue.fields.summary,
                                                                                                issue.fields.status)
            self.slack.send(recipient, message)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Jira Bot')
    parser.add_argument('--jira', help='Jira Server', required=True)
    parser.add_argument('--project', help='Jira Project ID', required=True)
    parser.add_argument('--label', help='Jira Label', required=True)
    parser.add_argument('--wip-limit', help='How many In Progress issues is too many?', default="3")
    parser.add_argument('--slack-key', help='The key for slack', required=True)
    args = parser.parse_args()

    jira = Jira(args.jira)
    slack = Slack(args.slack_key)
    bot = JiraBot(jira, slack, args.project, args.label, args.wip_limit)
    bot.start()
