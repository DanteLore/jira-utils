import logging
import unittest
import webbrowser

from charts.jira_charts import JiraCharts
from jira_utils.jira_utils import Jira
from tests.mock_jira import MockJira


class ChartTests(unittest.TestCase):
    def setUp(self):
        logger = logging.getLogger("JiraBot")
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
        logger.setLevel("DEBUG")
        logger.addHandler(stream_handler)
        self.jira = Jira("https://poo.atlassian.net", logger=logger).with_project("BIB").with_label("BRO")
        #self.jira = MockJira().with_n_fake_issues(50)

    def test_stories_closed_by_day(self):
        filename = JiraCharts(self.jira).stories_closed_per_day()
        webbrowser.open("file://" + filename)

    def test_stories_closed_by_week(self):
        filename = JiraCharts(self.jira).stories_closed_per_week()
        webbrowser.open("file://" + filename)
