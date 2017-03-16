from datetime import timedelta


class MetricsReport:
    def __init__(self, jira, title, start, end=None):
        self.jira = jira
        self.start = start
        self.end = end or self.start + timedelta(days=7)
        self.title = title

    def jira_server(self):
        return self.jira.server.replace("https://", "")

    def generate(self):
        title = self.title
        result = "Woop"

        return title, result
