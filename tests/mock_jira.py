import random
from datetime import datetime, timedelta
import dateutil.parser
import pytz


class MockIssue:
    class _MockIssueFields:
        def __init__(self, fields):
            self.id = fields.get("id")
            self.summary = fields.get("summary")
            self.assignee = fields.get("assignee")
            self.status = fields.get("status")
            self.project = fields.get("project")
            self.created = fields.get("created")
            self.updated = fields.get("updated")

    def __init__(self, fields):
        self.fields = self._MockIssueFields(fields)

    def __str__(self):
        return self.fields.id

    def __repr__(self):
        return self.fields.id


class MockJira:
    def __init__(self, issues=None, issue_objects=None, server=""):
        self.server = server

        if issue_objects is None:
            self.issues = []
        else:
            self.issues = issue_objects

        if issues is not None:
            for row in issues:
                issue = MockIssue(row)
                self.issues.append(issue)

    def with_n_fake_issues(self, n):
        new_issues = [{"id": "XXX-{0}".format(i), "summary": "x", "assignee": "x", "status": "Backlog"} for i in range(n)]
        return MockJira(issues=new_issues)

    def with_id(self, id):
        new_issues = filter(lambda i: i.fields.id == id, self.issues)
        return MockJira(issue_objects=new_issues)

    def with_these_ids(self, ids):
        new_issues = filter(lambda i: i.fields.id in ids, self.issues)
        return MockJira(issue_objects=new_issues)

    def with_project(self, _):
        return self

    def with_fix_version(self, _):
        return self

    def with_label(self, _):
        return self

    def order_by(self, _):
        return self

    def created_in_last_n_days(self, days):
        threshold = datetime.utcnow() - timedelta(days=days)
        threshold = pytz.UTC.localize(threshold)
        new_issues = filter(lambda i: i.fields.created is not None and dateutil.parser.parse(i.fields.created) >= threshold, self.issues)
        return MockJira(issue_objects=new_issues)

    def in_progress_for_n_days(self, days):
        # Since we're unable to access the status change gracefully in the mock, use Created Date instead
        # We're not testing the queries anyway - just the Bot logic!
        threshold = datetime.utcnow() - timedelta(days=days)
        threshold = pytz.UTC.localize(threshold)
        new_issues = filter(lambda i: i.fields.created is not None and dateutil.parser.parse(i.fields.created) <= threshold, self.issues)
        return MockJira(issue_objects=new_issues).status_is("In Progress")

    def resolved_n_days_ago(self, _):
        x = random.randint(0, len(self.issues))
        return MockJira(issue_objects=self.issues[x:])

    def created_n_days_ago(self, _):
        x = random.randint(0, len(self.issues))
        return MockJira(issue_objects=self.issues[x:])

    def open_issues_n_days_ago(self, _):
        x = random.randint(0, len(self.issues))
        return MockJira(issue_objects=self.issues[x:])

    def resolved_this_week(self):
        new_issues = filter(lambda i: i.fields.status.lower() == "done", self.issues)
        return MockJira(issue_objects=new_issues)

    def resolved_last_week(self):
        new_issues = filter(lambda i: i.fields.status.lower() == "done", self.issues)
        return MockJira(issue_objects=new_issues)

    def status_is_not(self, statuses):
        lower_statuses = map(lambda s: s.lower(), statuses)
        new_issues = filter(lambda i: i.fields.status.lower() not in lower_statuses, self.issues)
        return MockJira(issue_objects=new_issues)

    def status_is(self, status):
        new_issues = filter(lambda i: i.fields.status.lower() == status.lower(), self.issues)
        return MockJira(issue_objects=new_issues)

    def not_assigned(self):
        new_issues = filter(lambda i: i.fields.assignee is None or i.fields.assignee == "None", self.issues)
        return MockJira(issue_objects=new_issues)

    def assigned(self):
        new_issues = filter(lambda i: i.fields.assignee is not None and i.fields.assignee != "None", self.issues)
        return MockJira(issue_objects=new_issues)

    def get_issues(self):
        return self.issues

    def count_issues(self):
        return len(self.issues)
