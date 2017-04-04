import uuid
from datetime import timedelta
from itertools import groupby

import dateutil.parser


def date_extension(number):
    if number % 10 == 1:
        return '%dst' % number
    if number % 10 == 2:
        return '%dnd' % number
    if 11 <= number < 20:
        return '%dth' % number
    if number % 10 == 3:
        return '%drd' % number
    if (number % 10 >= 4) or (number % 10 == 0):
        return '%dth' % number


class KanbanReport:
    def __init__(self, jira, logger, title, start, end=None):
        self.jira = jira
        self.start = start
        self.end = end or self.start + timedelta(days=7)
        self.title = title
        self.logger = logger

    def jira_server(self):
        return self.jira.server.replace("https://", "")

    ISSUE_LIST = """
    <p>
        <ac:structured-macro ac:name="jira" ac:schema-version="1" ac:macro-id="{id}">
            <ac:parameter ac:name="server">JIRA({jira})</ac:parameter>
            <ac:parameter ac:name="columns">
                key,summary,created,resolved
            </ac:parameter>
            <ac:parameter ac:name="maximumIssues">{max_issues}</ac:parameter>
            <ac:parameter ac:name="jqlQuery">{jql}</ac:parameter>
            <ac:parameter ac:name="serverId">745d6455-8d95-39db-a8c7-48154b2e3f08</ac:parameter>
        </ac:structured-macro>
    </p>
    """

    SUMMARY_TABLE = """
    <table class="wrapped relative-table" style="width: 100%;">
        <colgroup>
            <col style="width: 20%;"/>
            <col style="width: 20%;"/>
            <col style="width: 20%;"/>
            <col style="width: 20%;"/>
            <col style="width: 20%;"/>
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
                <td style="font-size: 1.5em;">
                    Resolved this week: <span style="color: rgb(255,102,0);"><strong>{resolved}</strong></span>
                </td>
                <td style="font-size: 1.5em;">
                    Added this week: <span style="color: rgb(255,102,0);"><strong>{added}</strong></span>
                </td>
            </tr>
        </tbody>
    </table>
    """

    AGE_TABLE = """
    <table class="wrapped relative-table" style="width: 100%;">
        <colgroup>
            <col style="width: 25%;"/>
            <col style="width: 75%;"/>
        </colgroup>
        <tbody>
            <tr>
                <td style="font-size: 1.5em;">
                    Mean Age: <span style="color: rgb(255,102,0);"><strong>{mean}</strong></span>
                </td>
                <td rowspan="2">
                    {histogram}
                </td>
            </tr>
            <tr>
                <td style="font-size: 1.5em;">
                    Oldest: <span style="color: rgb(255,102,0);"><strong>{maximum}</strong></span>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    {issues}
                </td>
            </tr>
        </tbody>
    </table>
    """

    HISTOGRAM = """
    <ac:structured-macro ac:name="chart" ac:schema-version="1" ac:macro-id="0a37425e-ddd1-4bc6-ad1c-4a7c73451e0a">
        <ac:parameter ac:name="domainaxisrotateticklabel">true</ac:parameter>
        <ac:parameter ac:name="dateFormat">MM/yyyy</ac:parameter>
        <ac:parameter ac:name="timePeriod">Month</ac:parameter>
        <ac:parameter ac:name="rangeAxisLowerBound">0</ac:parameter>
        <ac:parameter ac:name="dataOrientation">vertical</ac:parameter>
        <ac:parameter ac:name="type">bar</ac:parameter>
        <ac:parameter ac:name="width">800</ac:parameter>
        <ac:parameter ac:name="height">300</ac:parameter>
        <ac:rich-text-body>
            <table>
                <tbody>
                    <tr>
                        <th><p>Age</p></th>
                        <th><p>Number of issues by age (days)</p></th>
                    </tr>

                    {data}

                </tbody>
            </table>
        </ac:rich-text-body>
    </ac:structured-macro>
    """

    def issue_list(self, query, max_issues=50):
        return self.ISSUE_LIST.format(
            id=str(uuid.uuid4()),
            jql=query.replace("<", "&lt;").replace(">", "&gt;"),
            jira=self.jira_server(),
            max_issues=max_issues
        )

    def age_table(self, query):
        issues = query.get_issues()

        total = 0
        maximum = 0
        count = 0
        for issue in issues:
            secs = (self.end - dateutil.parser.parse(issue.fields.created)).total_seconds()
            total += secs
            count += 1
            maximum = max(maximum, secs)

        if count == 0:
            return "<em>No Data</em>"

        mean = timedelta(seconds=total / count)
        maximum = timedelta(seconds=maximum)

        return self.AGE_TABLE.format(
            mean="{0} days".format(mean.days),
            maximum="{0} days".format(maximum.days),
            histogram=self.age_histogram(issues),
            issues=self.issue_list(query.jql, 5)
        )

    def age_histogram(self, issues):
        seconds = map(lambda issue: (self.end - dateutil.parser.parse(issue.fields.created)).total_seconds(), issues)
        days = map(lambda secs: timedelta(seconds=secs).days, seconds)
        maximum = max(days)

        if maximum > 300:
            step = 50
        elif maximum > 200:
            step = 20
        elif maximum > 90:
            step = 14
        elif maximum > 10:
            step = 5
        else:
            step = 1

        text = ""
        bottom = 0
        while bottom <= maximum:
            top = bottom + step
            count = len(filter(lambda d: bottom <= d < top, days))
            text += "<tr><td><p>{0}-{1}</p></td><td><p>{2}</p></td></tr>\n".format(bottom, top, count)
            bottom = top

        return self.HISTOGRAM.format(data=text)

    def group_issues(self, issues):
        def get_key(card):
            return str(card.fields.assignee)

        # You must SORT before you GROUP. Which is :poo:
        issues = sorted(list(issues), key=get_key)

        for name, cards in groupby(issues, key=get_key):
            yield (name, len(list(cards)))

    def leader_board(self, issues):
        groups = sorted(self.group_issues(issues), key=lambda i: i[1], reverse=True)

        result = '\n<ul>'
        for (name, count) in groups:
            result += '<li style="font-size: 1.5em;">{0}: <strong>{1}</strong></li>'.format(name, count)
        result += '</ul>\n'

        return result

    def generate(self):
        title = '{title} - {start} to {end}'.format(
            start=date_extension(self.start.day) + self.start.strftime(" %B"),
            end=date_extension(self.end.day) + self.end.strftime(" %B"),
            title=self.title
        )

        result = self.SUMMARY_TABLE.format(
            backlog=self.jira.status_was("BACKLOG", self.end).count_issues(),
            todo=self.jira.status_was("TO DO", self.end).count_issues(),
            inprogress=self.jira.status_was("IN PROGRESS", self.end).count_issues(),
            added=self.jira.created_between(self.start, self.end).count_issues(),
            resolved=self.jira.resolved_between(self.start, self.end).count_issues()
        )

        result += '<table class="wrapped relative-table" style="width: 100%;">'
        result += '<colgroup><col style="width: 50%;" /><col style="width: 50%;"/></colgroup>'
        result += '<tbody><tr><td><h2>Created this week</h2>'
        result += self.issue_list(self.jira.created_between(self.start, self.end).jql)
        result += '</td><td><h2>Resolved this week</h2>'
        result += self.issue_list(self.jira.resolved_between(self.start, self.end).jql)
        result += '</td></tr></tbody></table>'

        result += '<h1>Issues closed by</h1>'
        result += self.leader_board(self.jira.resolved_between(self.start, self.end).get_issues())

        result += '<h1>To Do:</h1>'
        result += self.age_table(self.jira.status_was("TO DO", self.end))
        result += '<h1>Backlog:</h1>'
        result += self.age_table(self.jira.status_was("BACKLOG", self.end))
        result += '<h1>Closed this week:</h1>'
        result += self.age_table(self.jira.resolved_between(self.start, self.end))

        return title, result
