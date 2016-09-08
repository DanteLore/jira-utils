import unittest

from freezegun import freeze_time

from bot.jirabot import JiraBot, MessageToJiraAttachmentConverter
from tests.mock_jira import MockJira
from tests.mock_slack import MockSlack


class JiraBotTests(unittest.TestCase):
    def test_no_messages_when_nothing_interesting_happening(self):
        jira = MockJira(issues=[
            {"id": "XXX-1", "summary": "My first Jira", "status": "Backlog"},
            {"id": "XXX-2", "summary": "My second Jira", "status": "Backlog"},
        ])
        slack = MockSlack()
        bot = JiraBot(jira, slack, "XXX", "LABEL", 3)
        bot.process()
        self.assertEqual(len(slack.messages), 0)

    def test_message_sent_if_issue_assigned_but_not_in_progress(self):
        jira = MockJira(issues=[
            {"id": "XXX-1", "summary": "My first Jira", "assignee": "Fred Bloggs", "status": "Backlog"},
            {"id": "XXX-2", "summary": "My second Jira", "assignee": "None", "status": "Backlog"},
            {"id": "XXX-3", "summary": "My third Jira", "assignee": "Fred Jones", "status": "In Progress"},
        ])
        slack = MockSlack()
        bot = JiraBot(jira, slack, "XXX", "LABEL", "#channel_name", 3)
        bot.process()
        self.assertEqual(len(slack.messages), 1)
        self.assertEqual("#channel_name", slack.messages[0]["recipient"])
        self.assertEqual(':warning: XXX-1 is assigned to *Fred Bloggs* but still in the Backlog state',
                         slack.messages[0]["message"])

    def test_message_sent_if_issue_in_progress_but_not_assigned(self):
        jira = MockJira(issues=[
            {"id": "XXX-1", "summary": "My first Jira", "assignee": "Cheesy Phil", "status": "In Progress"},
            {"id": "XXX-2", "summary": "My second Jira", "assignee": "None", "status": "In Progress"},
            {"id": "XXX-3", "summary": "My third Jira", "assignee": "Fred Jones", "status": "In Progress"},
        ])
        slack = MockSlack()
        bot = JiraBot(jira, slack, "XXX", "LABEL", "#the_channel")
        bot.process()
        self.assertEqual(1, len(slack.messages))
        self.assertEqual("#the_channel", slack.messages[0]["recipient"])
        self.assertEqual(":warning: XXX-2 is marked as In Progress but not assigned to anyone",
                         slack.messages[0]["message"])

    def test_message_sent_if_too_many_issues_in_progress(self):
        jira = MockJira(issues=[
            {"id": "XXX-1", "summary": "My first Jira", "assignee": "Busy Bob", "status": "In Progress"},
            {"id": "XXX-2", "summary": "My second Jira", "assignee": "Busy Bob", "status": "In Progress"},
            {"id": "XXX-3", "summary": "My third Jira", "assignee": "Busy Bob", "status": "In Progress"},
            {"id": "XXX-4", "summary": "My fourth Jira", "assignee": "Busy Bob", "status": "In Progress"},
            {"id": "XXX-5", "summary": "My fifth Jira", "assignee": "Busy Bob", "status": "In Progress"},
            {"id": "XXX-6", "summary": "My sixth Jira", "assignee": "Lazy Susan", "status": "In Progress"},
        ])
        slack = MockSlack()
        bot = JiraBot(jira, slack, "XXX", "LABEL", "#chan1", 3)
        bot.process()
        self.assertEqual(len(slack.messages), 1)
        self.assertEqual("#chan1", slack.messages[0]["recipient"])
        self.assertEqual(
            ":warning: *Busy Bob* currently has 5 jira issues in progress. That's too many. Here's a list: XXX-1, XXX-2, XXX-3, XXX-4, XXX-5",
            slack.messages[0]["message"])

    @freeze_time("2016-08-10 09:00:00")
    def test_new_issues_in_backlog_notified_on_channel(self):
        jira = MockJira(issues=[
            {"id": "AAA-2", "summary": "I am new", "status": "Backlog", "created": u'2016-08-10T07:55:00.000+0100'},
            {"id": "AAA-1", "summary": "I am not new", "status": "Backlog", "created": u'2016-08-08T14:50:36.000+0100'}
        ])
        slack = MockSlack()
        bot = JiraBot(jira, slack, "AAA", "LABEL", "#whatever")
        bot.process()
        self.assertEqual(1, len(slack.messages))
        self.assertEqual(':memo: New issue AAA-2 added', slack.messages[0]["message"])

    @freeze_time("2016-08-10 09:00:00")
    def test_new_issues_not_repeated_in_channel(self):
        jira = MockJira(issues=[
            {"id": "AAA-2", "summary": "I am new", "status": "Backlog", "created": u'2016-08-10T07:55:00.000+0100'},
            {"id": "AAA-1", "summary": "I am not new", "status": "Backlog", "created": u'2016-08-08T14:50:36.000+0100'}
        ])
        slack = MockSlack()
        bot = JiraBot(jira, slack, "AAA", "LABEL", "#things")
        bot.process()
        bot.process()
        self.assertEqual(1, len(slack.messages))

    def test_no_attachments_added_for_string_with_no_jira_ids(self):
        attachments = MessageToJiraAttachmentConverter(jira=MockJira()).apply(
            "This text doesn't contain any Jira IDs")
        self.assertEqual(0, len(attachments))

    def test_attachment_added_for_single_jira_id(self):
        jira = MockJira(server="https://myjira.atlassian.net",
                        issues=[
                            {"id": "XXX-123", "summary": "I am a Jira"}
                        ])
        output = MessageToJiraAttachmentConverter(jira).apply("The best Jira is XXX-123")
        self.assertEqual(1, len(output))
        self.assertEqual("https://myjira.atlassian.net/browse/XXX-123", output[0]["title_link"])
        self.assertEqual("XXX-123: I am a Jira", output[0]["title"])
