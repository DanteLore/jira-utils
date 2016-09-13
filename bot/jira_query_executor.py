class JiraQueryExecutor:
    def __init__(self, jira):
        self.jira = jira

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

    def get_backlog_issues(self):
        issues = self.jira.status_is("backlog").get_issues()
        ids = map(lambda i: "{0}".format(i), issues)
        if len(ids) > 0:
            message = ':memo: The following issues are currently on the *backlog*: {0}'.format(', '.join(ids))
        else:
            message = ':memo: The backlog is empty!'
        return message
