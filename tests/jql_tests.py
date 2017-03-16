import unittest

from jira_utils.jira_utils import Jira
from datetime import datetime

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

    def test_status_was(self):
        jira = Jira("").status_was("STATE X", datetime(2017, 1, 11))
        self.assertEqual('status was "STATE X" on "2017/01/11"', jira.jql)

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

    def test_resolved_since_8_days_ago(self):
        jira = Jira("").resolved_n_days_ago(8)
        self.assertEqual('resolutionDate >= startOfDay(-8d) and resolutionDate < endOfDay(-8d)', jira.jql)

    def test_resolved_since_2_days_ago(self):
        jira = Jira("").resolved_n_days_ago(2)
        self.assertEqual('resolutionDate >= startOfDay(-2d) and resolutionDate < endOfDay(-2d)', jira.jql)

    def test_resolved_this_week(self):
        jira = Jira("").resolved_this_week()
        self.assertEqual('resolutionDate >= startOfWeek()', jira.jql)

    def test_resolved_last_week(self):
        jira = Jira("").resolved_last_week()
        self.assertEqual('resolutionDate >= startOfWeek(-1w) and resolutionDate < endOfWeek(-1w)', jira.jql)

    def test_in_progress_for_7_days(self):
        jira = Jira("").in_progress_for_n_days(7)
        self.assertEqual('status changed to "In Progress" before -7d', jira.jql)

    def test_created_between(self):
        jira = Jira("").created_between(datetime(2017, 1, 1), datetime(2017, 1, 3))
        self.assertEqual('created >= "2017/01/01" and created < "2017/01/03"', jira.jql)

    def test_resolved_between(self):
        jira = Jira("").resolved_between(datetime(2017, 2, 2), datetime(2017, 2, 9))
        self.assertEqual('resolutionDate >= "2017/02/02" and resolutionDate < "2017/02/09"', jira.jql)

    def test_query_by_sub_team(self):
        jira = Jira("").with_sub_team("Teamsters")
        self.assertEqual('sub-team = "Teamsters"', jira.jql)
