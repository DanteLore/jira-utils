import unittest

from charts.jira_charts import JiraCharts
from jira_utils.jira_utils import Jira


class ChartTests(unittest.TestCase):
    def test_bar_chart(self):
        jira = Jira("https://poo.atlassian.net").with_project("BIB").with_label("BRO")

        JiraCharts(jira).stories_closed_per_day()
