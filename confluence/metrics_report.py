from datetime import timedelta, datetime


class MetricsReport:
    def __init__(self, jira, logger, title, start, end=None):
        self.jira = jira
        self.start = start
        self.end = end or self.start + timedelta(weeks=52)
        self.title = title
        self.logger = logger

    def jira_server(self):
        return self.jira.server.replace("https://", "")

    OPEN_CLOSED_CHART = """
    <ac:structured-macro ac:name="chart" ac:schema-version="1" ac:macro-id="0a37425e-ddd1-4bc6-ad1c-4a7c73451e0a">
        <ac:parameter ac:name="domainaxisrotateticklabel">true</ac:parameter>
        <ac:parameter ac:name="dateFormat">MM/yyyy</ac:parameter>
        <ac:parameter ac:name="timePeriod">Week</ac:parameter>
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

    CUMULATIVE_FLOW_CHART = """
    <ac:structured-macro ac:name="chart" ac:schema-version="1" ac:macro-id="0a37425e-ddd1-4bc6-ad1c-4a7c73451e0a">
        <ac:parameter ac:name="domainaxisrotateticklabel">true</ac:parameter>
        <ac:parameter ac:name="timeseries">true</ac:parameter>
        <ac:parameter ac:name="dateFormat">dd/MM/yy</ac:parameter>
        <ac:parameter ac:name="timePeriod">Week</ac:parameter>
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
                <td colspan="3" style="font-size: 1.5em;">
                    Open Issues: <span style="color: rgb(102,102,255); font-size: 3em;"><strong>{open_issues}</strong></span>
                </td>
            </tr>
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
                    <p style="font-size: 0.8em;">(<em>Backlog</em>, <em>To Do</em> and <em>In Progress</em> counts by week)</p>

                    {flow}
                </td>
            </tr>
        </tbody>
    </table>
    """

    def table_line(self, x, end):
        return "<tr><td><p>{end}</p></td><td><p>{x}</p></td></tr>\n".format(
            end=end.strftime("%d-%m-%y"),
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

            closed_lines += self.table_line(closed_count, end)
            added_lines += self.table_line(added_count, end)
            delta_lines += self.table_line(added_count - closed_count, end)

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
            backlog_lines += self.table_line(self.jira.status_was("BACKLOG", end).count_issues(), end)
            todo_lines += self.table_line(self.jira.status_was("TO DO", end).count_issues(), end)
            in_progress_lines += self.table_line(self.jira.status_was("IN PROGRESS", end).count_issues(), end)

            start = start + timedelta(days=7)
            end = start + timedelta(days=7)
        result = "<p>"
        result += self.CUMULATIVE_FLOW_CHART.format(backlog=backlog_lines, todo=todo_lines,
                                                    inprogress=in_progress_lines)
        result += "</p>"
        return result

    def generate(self):
        title = self.title

        backlog_count = self.jira.status_was("BACKLOG", self.end).count_issues()
        todo_count = self.jira.status_was("TO DO", self.end).count_issues()
        inprog_count = self.jira.status_was("IN PROGRESS", self.end).count_issues()
        open_count = backlog_count + todo_count + inprog_count

        result = "<h1>Maintenance</h1>"
        result += "<p>Report for week ending *{end}* generated {now}</p>".format(
            end=(self.end - timedelta(days=1)).strftime("%d-%m-%y"),
            now=datetime.now().strftime("%d-%m-%y")
        )
        result += self.PROJECT_TABLE.format(
            backlog=backlog_count,
            todo=todo_count,
            inprogress=inprog_count,
            open_issues=open_count,
            added=self.jira.created_between(self.end - timedelta(weeks=1), self.end).count_issues(),
            resolved=self.jira.resolved_between(self.end - timedelta(weeks=1), self.end).count_issues(),
            flow=self.cumulative_flow_chart()
        )

        # result += self.created_resolved_charts()
        # result += self.cumulative_flow_chart()

        return title, result
