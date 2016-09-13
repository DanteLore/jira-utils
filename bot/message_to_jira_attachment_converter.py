import re


class MessageToJiraAttachmentConverter:
    def __init__(self, jira):
        self.jira = jira
        self.format_str = "{0}/browse/{{0}}".format(jira.server.rstrip('/'))
        self.pattern = re.compile("([A-Z]+-[0-9]+)")

    def get_attachments(self, message):
        ids = self.pattern.findall(message)
        if len(ids) > 0:
            issues = self.jira.with_these_ids(ids).order_by("Rank").get_issues()

            for issue in issues:
                yield {
                    "fallback": "{0}: {1}".format(issue, issue.fields.summary),
                    "pretext": "",
                    "title": "{0}: {1}".format(issue, issue.fields.summary),
                    "title_link": self.format_str.format(issue),
                    "text": "Assigned: {0} Status: {1}".format(issue.fields.assignee or "-", issue.fields.status)
                }

    def apply(self, message):
        return list(self.get_attachments(message))
