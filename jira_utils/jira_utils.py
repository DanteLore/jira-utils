import logging

from jira import JIRA


class Jira:
    def __init__(self, server, jql="", logger=None):
        # Username and password go in the ~/.netrc file
        self.server = server
        self.jql = jql
        self.jira = None

        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger("TESTING")
            self.logger.setLevel("DEBUG")
            self.logger.addHandler(logging.StreamHandler())

    def join(self, fragment):
        if self.jql == "":
            return fragment
        else:
            return "{0} and {1}".format(self.jql, fragment)

    def with_id(self, id):
        fragment = 'id = "{0}"'.format(id)
        return Jira(self.server, self.join(fragment), logger=self.logger)

    def with_these_ids(self, ids):
        id_str = ", ".join(map(lambda s: '"{0}"'.format(s), ids))
        fragment = 'id in ({0})'.format(id_str)
        return Jira(self.server, self.join(fragment), logger=self.logger)

    def with_project(self, project):
        fragment = 'project = "{0}"'.format(project)
        return Jira(self.server, self.join(fragment), logger=self.logger)

    def with_label(self, label):
        fragment = 'labels in ("{0}")'.format(label)
        return Jira(self.server, self.join(fragment), logger=self.logger)

    def status_is_not(self, statuses):
        state_str = ", ".join(map(lambda s: '"{0}"'.format(s), statuses))
        fragment = 'status not in ({0})'.format(state_str)
        return Jira(self.server, self.join(fragment), logger=self.logger)

    def status_is(self, status):
        fragment = 'status = "{0}"'.format(status)
        return Jira(self.server, self.join(fragment), logger=self.logger)

    def not_assigned(self):
        return Jira(self.server, self.join('assignee is empty'), logger=self.logger)

    def assigned(self):
        return Jira(self.server, self.join('assignee is not empty'), logger=self.logger)

    def created_in_last_n_days(self, days):
        return Jira(self.server, self.join('created >= -{0}d'.format(days)), logger=self.logger)

    def order_by(self, field):
        return Jira(self.server, self.jql + ' order by {0}'.format(field), logger=self.logger)

    def count_issues(self):
        return len(self.get_issues())

    def get_issues(self):
        if self.jira is None:
            options = {
                'server': self.server
            }
            self.jira = JIRA(options)
        self.logger.debug("Executing JQL query: '{0}'".format(self.jql))
        return self.jira.search_issues(self.jql, maxResults=100)
