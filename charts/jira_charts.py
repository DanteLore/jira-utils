import logging
import os
import re
from datetime import datetime, timedelta
from distutils.dir_util import mkpath

from charts.bar_chart import BarChart
from charts.size_and_change_chart import SizeAndChangeChart


class JiraCharts:
    def __init__(self, jira, logger=None):
        self.jira = jira

        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger("TESTING")
            self.logger.setLevel("DEBUG")
            self.logger.addHandler(logging.StreamHandler())

    def get_temp_filename(self, title = "chart"):
        path = datetime.now().strftime("/tmp/jira-charts/{0}/%Y/%m/%d/%h").format(os.getpid())
        mkpath(path)
        title = re.sub("[^a-zA-Z0-9]", "_", title)
        filename = "{0}/{1}.png".format(path, title)
        return filename

    def stories_closed_per_day(self, report_range=7, title="Stories Closed by Day", force=False):
        filename = self.get_temp_filename("{0} {1}".format(title, report_range))

        if not os.path.exists(filename) or force:
            today = datetime.today()
            offsets = [x for x in range(report_range, -1, -1) if (today - timedelta(days=x)).weekday() not in [5, 6]]
            days = [(today - timedelta(days=x)).strftime('%A') for x in offsets]
            issue_counts = [self.jira.resolved_n_days_ago(x).count_issues() for x in offsets]

            chart = BarChart(days, issue_counts, title)
            chart.save_to_file(filename)

        return filename

    def stories_closed_per_week(self, report_range=6, title="Stories Closed by Week", force=False):
        filename = self.get_temp_filename("{0} {1}".format(title, report_range))

        if not os.path.exists(filename) or force:
            today = datetime.today()
            offsets = [x for x in range(report_range, -1, -1)]
            dates = [(today - timedelta(days=x*7)).strftime('%d/%m') for x in offsets]
            issue_counts = [self.jira.resolved_n_weeks_ago(x).count_issues() for x in offsets]

            chart = BarChart(dates, issue_counts, title)
            chart.save_to_file(filename)

        return filename

    def progress_by_day(self, report_range=31, title="Stories Closed vs Stories Added by Day", force=False):
        filename = self.get_temp_filename("{0} {1}".format(title, report_range))

        if not os.path.exists(filename) or force:
            today = datetime.today()
            offsets = [x for x in range(report_range, -1, -1) if (today - timedelta(days=x)).weekday() not in [5, 6]]
            days = [(today - timedelta(days=x)).strftime('%d/%m') for x in offsets]
            size_data = [self.jira.open_issues_n_days_ago(x).count_issues() for x in offsets]
            issues_closed = [self.jira.resolved_n_days_ago(x).count_issues() for x in offsets]
            issues_added = [-1 * self.jira.created_n_days_ago(x).count_issues() for x in offsets]

            chart = SizeAndChangeChart(days, issues_closed, issues_added, size_data, title)
            chart.save_to_file(filename)

        return filename
