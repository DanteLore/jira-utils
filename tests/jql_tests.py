import unittest

from jira_utils.jira_utils import Jira


class JiraJqlGenerationTests(unittest.TestCase):
    def test_project_filter(self):
        jira = Jira("").with_project("TEST")
        self.assertEqual('project = "TEST"', jira.jql)

    def test_label_filter(self):
        jira = Jira("").with_label("LAB1")
        self.assertEqual('labels in ("LAB1")', jira.jql)

    def test_project_and_label(self):
        jira = Jira("").with_project("PRJ").with_label("LBL")
        self.assertEqual('project = "PRJ" and labels in ("LBL")', jira.jql)

    def test_assigned(self):
        jira = Jira("").assigned()
        self.assertEqual('assignee is not empty', jira.jql)

    def test_not_assigned(self):
        jira = Jira("").not_assigned()
        self.assertEqual('assignee is empty', jira.jql)

    def test_status_is(self):
        jira = Jira("").status_is("STATE X")
        self.assertEqual('status = "STATE X"', jira.jql)

    def test_status_is_not(self):
        jira = Jira("").status_is_not(["STATE1", "STATE2"])
        self.assertEqual('status not in ("STATE1", "STATE2")', jira.jql)

    def test_longer_join(self):
        jira = Jira("").status_is_not(["S1", "S2"]).not_assigned().with_label("MYLABEL")
        self.assertEqual('status not in ("S1", "S2") and assignee is empty and labels in ("MYLABEL")', jira.jql)

