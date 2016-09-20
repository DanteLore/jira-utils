from itertools import groupby


class JiraWarningDetector:
    def __init__(self, jira, slack, project, label, logger, wip_limit=5, wip_time_limit=7):
        self.wip_limit = wip_limit
        self.wip_time_limit = wip_time_limit
        self.label = label
        self.project = project
        self.jira = jira
        self.slack = slack
        self.logger = logger

    def find_warnings(self):
        warnings = list(self.assigned_but_not_in_progress())
        warnings += list(self.too_many_in_progress())
        warnings += list(self.in_progress_but_not_assigned())
        warnings += list(self.in_progress_for_too_long())
        return warnings

    def too_many_in_progress(self):
        issues = self.jira.status_is("In Progress").assigned().get_issues()
        for k, v in groupby(issues, lambda i: i.fields.assignee):
            ids = map(lambda x: "{0}".format(x), list(v))
            self.logger.debug("{0} has {1} issues in progress".format(k, len(ids)))
            if len(ids) >= self.wip_limit:
                msg = ":warning: {0} currently has {1} jira issues in progress. That's too many. Here's a list: {2}".format(
                    self.format_user_mention(k),
                    len(ids),
                    ", ".join(ids)
                )
                yield msg

    def format_user_mention(self, user_name):
        user_id = self.slack.search_user_id(user_name)
        if user_id:
            user = "<@{0}>".format(user_id)
        else:
            user = "*{0}*".format(user_name)
        return user

    def assigned_but_not_in_progress(self):
        issues = self.jira \
            .status_is_not(["in progress", "done", "closed"]) \
            .assigned() \
            .get_issues()
        for issue in issues:
            assignee = issue.fields.assignee
            message = ':warning: {0} is assigned to {1} but still in the {2} state'.format(
                issue,
                self.format_user_mention(assignee),
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

    def in_progress_for_too_long(self):
        issues = self.jira \
            .status_is("in progress") \
            .in_progress_for_n_days(self.wip_time_limit) \
            .get_issues()

        self.logger.debug("Found {0} issues in progress for longer than {1} days".format(len(issues), self.wip_time_limit))
        for issue in issues:
            assignee = issue.fields.assignee
            message = ':clock2: {0} has been in progress for longer than 7 days. Is it blocked, {1}?'.format(
                issue,
                self.format_user_mention(assignee))
            yield message
