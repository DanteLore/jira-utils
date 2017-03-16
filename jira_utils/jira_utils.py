import logging

from jira import JIRA


class Jira:
    def __init__(self, server, jql="", logger=None):
        # Username and password go in the ~/.netrc file
        self.server = server
        self.jql = jql
        self.jira = None

        self.fields = ["id","summary","assignee","status","project","created","updated"]

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

    def with_fix_version(self, fix_version):
        fragment = 'fixVersion = "{0}"'.format(fix_version)
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

    def status_was(self, status, dt):
        fragment = 'status was "{status}" on "{date}"'.format(
            status=status,
            date=dt.strftime("%Y/%m/%d"))
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
        return len(self.get_issues(["id,summary"]))

    def get_issues(self, fields_to_use=None):
        if self.jira is None:
            options = {
                'server': self.server
            }
            self.jira = JIRA(options)

        if not fields_to_use:
            fields_to_use = self.fields

        self.logger.debug("Executing JQL query: '{0}'".format(self.jql))
        results = self.jira.search_issues(self.jql, fields=fields_to_use, maxResults=1000)
        self.logger.debug("Fetched {0} results".format(len(results)))
        return results

    def resolved_n_days_ago(self, day):
        fragment = "resolutionDate >= startOfDay(-{0}d) and resolutionDate < endOfDay(-{0}d)".format(day)
        return Jira(self.server, self.join(fragment), logger=self.logger)

    def created_n_days_ago(self, day):
        fragment = "created >= startOfDay(-{0}d) and created < endOfDay(-{0}d)".format(day)
        return Jira(self.server, self.join(fragment), logger=self.logger)

    def open_issues_n_days_ago(self, day):
        fragment = '(status was not in ("Done", "Closed") before endOfDay(-{0}d)) and created < endOfDay(-{0}d)'.format(day)
        return Jira(self.server, self.join(fragment), logger=self.logger)

    def resolved_this_week(self):
        fragment = "resolutionDate >= startOfWeek()"
        return Jira(self.server, self.join(fragment), logger=self.logger)

    def resolved_last_week(self):
        fragment = "resolutionDate >= startOfWeek(-1w) and resolutionDate < endOfWeek(-1w)"
        return Jira(self.server, self.join(fragment), logger=self.logger)

    def in_progress_for_n_days(self, days):
        fragment = 'status changed to "In Progress" before -{0}d'.format(days)
        return Jira(self.server, self.join(fragment), logger=self.logger)

    def created_between(self, start, end):
        fragment = 'created >= "{start}" and created < "{end}"'.format(
            start=start.strftime("%Y/%m/%d"),
            end=end.strftime("%Y/%m/%d")
        )
        return Jira(self.server, self.join(fragment), logger=self.logger)

    def resolved_between(self, start, end):
        fragment = 'resolutionDate >= "{start}" and resolutionDate < "{end}"'.format(
            start=start.strftime("%Y/%m/%d"),
            end=end.strftime("%Y/%m/%d")
        )
        return Jira(self.server, self.join(fragment), logger=self.logger)

    def with_sub_team(self, team):
        fragment = 'sub-team = "{0}"'.format(team)
        return Jira(self.server, self.join(fragment), logger=self.logger)
