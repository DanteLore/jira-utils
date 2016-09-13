from itertools import groupby


class JiraWarningDetector:
    def __init__(self, jira, project, label, logger, wip_limit=5):
        self.wip_limit = wip_limit
        self.label = label
        self.project = project
        self.jira = jira
        self.logger = logger

    def find_warnings(self):
        warnings = list(self.assigned_but_not_in_progress())
        warnings += list(self.too_many_in_progress())
        warnings += list(self.in_progress_but_not_assigned())
        return warnings

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
                yield msg

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
            yield message

    def in_progress_but_not_assigned(self):
        issues = self.jira \
            .status_is("in progress") \
            .not_assigned() \
            .get_issues()
        for issue in issues:
            message = ':warning: {0} is marked as In Progress but not assigned to anyone'.format(issue)
            yield message