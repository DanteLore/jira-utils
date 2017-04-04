from datetime import timedelta


class MetricsReport:
    def __init__(self, jira, logger, title, start, end=None):
        self.jira = jira
        self.start = start
        self.end = end or self.start + timedelta(weeks=20)
        self.title = title
        self.logger = logger

    def jira_server(self):
        return self.jira.server.replace("https://", "")

    OPEN_CLOSED_CHART = """
    <ac:structured-macro ac:name="chart" ac:schema-version="1" ac:macro-id="0a37425e-ddd1-4bc6-ad1c-4a7c73451e0a">
        <ac:parameter ac:name="domainaxisrotateticklabel">true</ac:parameter>
        <ac:parameter ac:name="dateFormat">MM/yyyy</ac:parameter>
        <ac:parameter ac:name="timePeriod">Month</ac:parameter>
        <ac:parameter ac:name="rangeAxisLowerBound">0</ac:parameter>
        <ac:parameter ac:name="dataOrientation">vertical</ac:parameter>
        <ac:parameter ac:name="type">line</ac:parameter>
        <ac:parameter ac:name="width">1200</ac:parameter>
        <ac:parameter ac:name="height">400</ac:parameter>
        <ac:rich-text-body>
            <table>
                <tbody>
                    <tr>
                        <th><p>Week</p></th>
                        <th><p>Issues closed per week</p></th>
                    </tr>

                    {closed}

                </tbody>
            </table>
            <table>
                <tbody>
                    <tr>
                        <th><p>Week</p></th>
                        <th><p>Issues added per week</p></th>
                    </tr>

                    {added}

                </tbody>
            </table>
        </ac:rich-text-body>
    </ac:structured-macro>
    """

    DELTA_CHART = """
    <ac:structured-macro ac:name="chart" ac:schema-version="1" ac:macro-id="0a37425e-ddd1-4bc6-ad1c-4a7c73451e0a">
        <ac:parameter ac:name="domainaxisrotateticklabel">true</ac:parameter>
        <ac:parameter ac:name="dateFormat">MM/yyyy</ac:parameter>
        <ac:parameter ac:name="timePeriod">Month</ac:parameter>
        <ac:parameter ac:name="dataOrientation">vertical</ac:parameter>
        <ac:parameter ac:name="type">bar</ac:parameter>
        <ac:parameter ac:name="width">1200</ac:parameter>
        <ac:parameter ac:name="height">400</ac:parameter>
        <ac:rich-text-body>
            <table>
                <tbody>
                    <tr>
                        <th><p>Week</p></th>
                        <th><p>Backlog change by week</p></th>
                    </tr>

                    {data}

                </tbody>
            </table>
        </ac:rich-text-body>
    </ac:structured-macro>
    """

    BACKLOG_CHART = """
    <ac:structured-macro ac:name="chart" ac:schema-version="1" ac:macro-id="0a37425e-ddd1-4bc6-ad1c-4a7c73451e0a">
        <ac:parameter ac:name="domainaxisrotateticklabel">true</ac:parameter>
        <ac:parameter ac:name="dateFormat">MM/yyyy</ac:parameter>
        <ac:parameter ac:name="timePeriod">Month</ac:parameter>
        <ac:parameter ac:name="dataOrientation">vertical</ac:parameter>
        <ac:parameter ac:name="type">area</ac:parameter>
        <ac:parameter ac:name="stacked">true</ac:parameter>
        <ac:parameter ac:name="width">1200</ac:parameter>
        <ac:parameter ac:name="height">400</ac:parameter>
        <ac:rich-text-body>
            <table>
                <tbody>
                    <tr><th><p>Week</p></th><th><p>Backlog</p></th></tr>
                    {backlog}
                </tbody>
            </table>
            <table>
                <tbody>
                    <tr><th><p>Week</p></th><th><p>To Do</p></th></tr>
                    {todo}
                </tbody>
            </table>
            <table>
                <tbody>
                    <tr><th><p>Week</p></th><th><p>In Progress</p></th></tr>
                    {inprogress}
                </tbody>
            </table>
        </ac:rich-text-body>
    </ac:structured-macro>
    """

    PROJECT_TABLE = """
    <table class="wrapped relative-table" style="width: 100%;">
        <colgroup>
            <col style="width: 33%;"/>
            <col style="width: 33%;"/>
            <col style="width: 34%;"/>
        </colgroup>
        <tbody>
            <tr>
                <td style="font-size: 1.5em;">
                    Backlog: <span style="color: rgb(255,102,0);"><strong>{backlog}</strong></span>
                </td>
                <td style="font-size: 1.5em;">
                    To do: <span style="color: rgb(255,102,0);"><strong>{todo}</strong></span>
                </td>
                <td style="font-size: 1.5em;">
                    In progress: <span style="color: rgb(255,102,0);"><strong>{inprogress}</strong></span>
                </td>
            </tr>
            <tr>
                <td style="font-size: 1.5em;">
                    Resolved this week: <span style="color: rgb(255,102,0);"><strong>{resolved}</strong></span>
                </td>
                <td style="font-size: 1.5em;">
                    Added this week: <span style="color: rgb(255,102,0);"><strong>{added}</strong></span>
                </td>
                <td>
                    &nbsp;
                </td>
            </tr>
            <tr>
                <td colspan="3">
                    <p style="font-size: 1.5em;">12 Month Cumulative Flow</p>
                    <p style="font-size: 0.5em;">(<em>Backlog</em>, <em>To Do</em> and <em>In Progress</em> counts by week)</p>

                    {flow}
                </td>
            </tr>
        </tbody>
    </table>
    """

    def table_line(self, x, end, start):
        return "<tr><td><p>{start}-{end}</p></td><td><p>{x}</p></td></tr>\n".format(
            start=start.strftime("%d-%m"),
            end=end.strftime("%d-%m"),
            x=x
        )

    def created_resolved_charts(self):
        closed_lines = ""
        added_lines = ""
        delta_lines = ""

        start = self.start
        end = start + timedelta(days=7)
        while end <= self.end:
            self.logger.info("Created/Resolved Chart: fetching {0} to {1}".format(start.date(), end.date()))

            closed_count = self.jira.resolved_between(start, end).count_issues()
            added_count = self.jira.created_between(start, end).count_issues()

            closed_lines += self.table_line(closed_count, end, start)
            added_lines += self.table_line(added_count, end, start)
            delta_lines += self.table_line(added_count - closed_count, end, start)

            start = start + timedelta(days=7)
            end = start + timedelta(days=7)

        result = "<p>"
        result += self.OPEN_CLOSED_CHART.format(closed=closed_lines, added=added_lines)
        result += "</p>\n<p>"
        result += self.DELTA_CHART.format(data=delta_lines)
        result += "</p>"
        return result

    def cumulative_flow_chart(self):
        backlog_lines = ""
        todo_lines = ""
        in_progress_lines = ""
        start = self.start
        end = start + timedelta(days=7)
        while end <= self.end:
            self.logger.info("Cumulative Flow Chart: fetching {0} to {1}".format(start.date(), end.date()))
            backlog_lines += self.table_line(self.jira.status_was("BACKLOG", end).count_issues(), end, start)
            todo_lines += self.table_line(self.jira.status_was("TO DO", end).count_issues(), end, start)
            in_progress_lines += self.table_line(self.jira.status_was("IN PROGRESS", end).count_issues(), end, start)

            start = start + timedelta(days=7)
            end = start + timedelta(days=7)
        result = "<p>"
        result += self.BACKLOG_CHART.format(backlog=backlog_lines, todo=todo_lines, inprogress=in_progress_lines)
        result += "</p>"
        return result

    def generate(self):
        title = self.title

        result = "<h1>Maintenance</h1>"
        result += self.PROJECT_TABLE.format(
            backlog=self.jira.status_was("BACKLOG", self.end).count_issues(),
            todo=self.jira.status_was("TO DO", self.end).count_issues(),
            inprogress=self.jira.status_was("IN PROGRESS", self.end).count_issues(),
            added=self.jira.created_between(self.end - timedelta(weeks=1), self.end).count_issues(),
            resolved=self.jira.resolved_between(self.end - timedelta(weeks=1), self.end).count_issues(),
            flow=self.cumulative_flow_chart()
        )

        # result += self.created_resolved_charts()
        # result += self.cumulative_flow_chart()

        return title, result
