import unittest

from jira_utils.jira_utils import Jira


class JiraJqlGenerationTests(unittest.TestCase):
    def order_by_rank(self):
        jira = Jira("").order_by("Rank")
        self.assertEqual('order by rank', jira.jql)

    def test_project_filter(self):
        jira = Jira("").with_project("TEST")
        self.assertEqual('project = "TEST"', jira.jql)

    def test_query_by_id(self):
        jira = Jira("").with_id("XXX-470")
        self.assertEqual('id = "XXX-470"', jira.jql)

    def test_query_by_ids(self):
        jira = Jira("").with_these_ids(["XXX-470", "YYY-111"])
        self.assertEqual('id in ("XXX-470", "YYY-111")', jira.jql)

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

    def test_created_since_1_day_ago(self):
        jira = Jira("").created_in_last_n_days(1)
        self.assertEqual('created >= -1d', jira.jql)

    def test_created_since_8_days_ago(self):
        jira = Jira("").created_in_last_n_days(8)
        self.assertEqual('created >= -8d', jira.jql)

    def resolved_since_8_days_ago(self):
        jira = Jira("").resolved_n_days_ago(8)
        self.assertEqual('resolutionDate >= startOfDay(-8d) and resolutionDate < endOfDay(-8d)', jira.jql)

    def resolved_since_2_days_ago(self):
        jira = Jira("").resolved_n_days_ago(2)
        self.assertEqual('resolutionDate >= startOfDay(-2d) and resolutionDate < endOfDay(-2d)', jira.jql)

    def in_progress_for_7_days(self):
        jira = Jira("").in_progress_for_n_days(7)
        self.assertEqual('status changed to "In Progress" before -7d', jira.jql)
