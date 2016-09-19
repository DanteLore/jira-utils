class JiraQueryExecutor:
    def __init__(self, jira):
        self.jira = jira

    def get_new_issues_on_backlog(self):
        issues = self.jira.status_is_not(["in progress", "done", "closed"]).created_in_last_n_days(1).order_by("Rank").get_issues()
        for issue in issues:
            yield (':memo: New issue {0} added'.format(issue))

    def get_new_issues_summary(self):
        issues = self.jira.status_is_not(["in progress", "done", "closed"]).created_in_last_n_days(1).order_by("Rank").get_issues()
        ids = map(lambda i: "{0}".format(i), issues)
        if len(ids):
            return ':memo: The following *new issues* issues have been added in the last 24 hours: {0}'.format(', '.join(ids))
        else:
            return ':memo: No issues added in the last 24 hours'

    def get_in_progress_issues(self):
        issues = self.jira.status_is("in progress").order_by("Rank").get_issues()
        ids = map(lambda i: "{0}".format(i), issues)
        if len(ids) > 0:
            return ':memo: The following issues are currently *in progress*: {0}'.format(', '.join(ids))
        else:
            return ':memo: Nothing currently marked as in progress!'

    def get_to_do_issues(self):
        issues = self.jira.status_is("to do").order_by("Rank").get_issues()
        ids = map(lambda i: "{0}".format(i), issues)
        if len(ids) > 0:
            return ':memo: The following issues are currently on the *to do list*: {0}'.format(', '.join(ids))
        else:
            return ':memo: The To Do list is empty!'

    def get_backlog_issues(self):
        issues = self.jira.status_is("backlog").order_by("Rank").get_issues()
        ids = map(lambda i: "{0}".format(i), issues)
        if len(ids) > 0:
            return ':memo: The following issues are currently on the *backlog*: {0}'.format(', '.join(ids))
        else:
            return ':memo: The backlog is empty!'

    def get_status_summary(self):
        backlog_size = self.jira.status_is("Backlog").count_issues()
        to_do_size = self.jira.status_is("To Do").count_issues()
        in_progress_size = self.jira.status_is("In Progress").count_issues()
        message = "Here's a summary of where we are right now in Jira:\nBacklog: *{0}*\nTo Do: *{1}*\nIn Progress: *{2}*"\
            .format(backlog_size, to_do_size, in_progress_size)
        return message
