from jira import JIRA


class Jira:
    def __init__(self, server, jql=""):
        # Username and password go in the ~/.netrc file
        self.server = server
        self.jql = jql
        self.jira = None

    def join(self, fragment):
        if self.jql == "":
            return fragment
        else:
            return "{0} and {1}".format(self.jql, fragment)

    def with_project(self, project):
        fragment = 'project = "{0}"'.format(project)
        return Jira(self.server, self.join(fragment))

    def with_label(self, label):
        fragment = 'labels in ("{0}")'.format(label)
        return Jira(self.server, self.join(fragment))

    def status_is_not(self, statuses):
        state_str = ", ".join(map(lambda s: '"{0}"'.format(s), statuses))
        fragment = 'status not in ({0})'.format(state_str)
        return Jira(self.server, self.join(fragment))

    def status_is(self, status):
        fragment = 'status = "{0}"'.format(status)
        return Jira(self.server, self.join(fragment))

    def not_assigned(self):
        return Jira(self.server, self.join('assignee is empty'))

    def assigned(self):
        return Jira(self.server, self.join('assignee is not empty'))

    def get_issues(self):
        if self.jira is None:
            options = {
                'server': self.server
            }
            self.jira = JIRA(options)
        return self.jira.search_issues(self.jql, maxResults=100)