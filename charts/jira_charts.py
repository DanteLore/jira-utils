import logging
import tempfile
from datetime import datetime, timedelta

from charts.bar_chart import BarChart


class JiraCharts:
    def __init__(self, jira, logger=None):
        self.jira = jira

        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger("TESTING")
            self.logger.setLevel("DEBUG")
            self.logger.addHandler(logging.StreamHandler())

    def get_temp_filename(self):
        return tempfile.mktemp(suffix=".png")

    def stories_closed_per_day(self, report_range=7):
        filename = self.get_temp_filename()

        today = datetime.today()
        offsets = [x for x in range(report_range, -1, -1) if (today - timedelta(days=x)).weekday() not in [5, 6]]
        days = [(today - timedelta(days=x)).strftime('%A') for x in offsets]
        issue_counts = [self.jira.resolved_n_days_ago(x).count_issues() for x in offsets]

        chart = BarChart(days, issue_counts, title="Stories Closed by Day")
        chart.save_to_file(filename)

        return filename

    def stories_closed_per_week(self, report_range=6):
        filename = self.get_temp_filename()

        today = datetime.today()
        offsets = [x for x in range(report_range, -1, -1)]
        days = [(today - timedelta(days=x*7)).strftime('%d/%m') for x in offsets]
        issue_counts = [self.jira.resolved_n_weeks_ago(x).count_issues() for x in offsets]

        chart = BarChart(days, issue_counts, title="Stories Closed by Week")
        chart.save_to_file(filename)

        return filename
