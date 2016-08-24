import unittest

from bot.jirabot import JiraBot
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
        bot.start()
        self.assertEqual(len(slack.messages), 0)

    def test_message_sent_if_issue_assigned_but_not_in_progress(self):
        jira = MockJira(issues=[
            {"id": "XXX-1", "summary": "My first Jira", "assignee": "Fred Bloggs", "status": "Backlog"},
            {"id": "XXX-2", "summary": "My second Jira", "assignee": "None", "status": "Backlog"},
            {"id": "XXX-3", "summary": "My third Jira", "assignee": "Fred Jones", "status": "In Progress"},
        ])
        slack = MockSlack()
        bot = JiraBot(jira, slack, "XXX", "LABEL", 3)
        bot.start()
        self.assertEqual(len(slack.messages), 1)
        self.assertEqual("Fred Bloggs", slack.messages[0]["recipient"])
        self.assertEqual('Warning: XXX-1 "My first Jira" is assigned to you but still in the Backlog state',
                         slack.messages[0]["message"])

    def test_message_sent_if_too_many_issues_in_progress(self):
        jira = MockJira(issues=[
            {"id": "XXX-1", "summary": "My first Jira",  "assignee": "Busy Bob", "status": "In Progress"},
            {"id": "XXX-2", "summary": "My second Jira", "assignee": "Busy Bob", "status": "In Progress"},
            {"id": "XXX-3", "summary": "My third Jira",  "assignee": "Busy Bob", "status": "In Progress"},
            {"id": "XXX-4", "summary": "My fourth Jira", "assignee": "Busy Bob", "status": "In Progress"},
            {"id": "XXX-5", "summary": "My fifth Jira",  "assignee": "Busy Bob", "status": "In Progress"},
            {"id": "XXX-6", "summary": "My sixth Jira",  "assignee": "Lazy Susan", "status": "In Progress"},
        ])
        slack = MockSlack()
        bot = JiraBot(jira, slack, "XXX", "LABEL", 3)
        bot.start()
        self.assertEqual(len(slack.messages), 1)
        self.assertEqual("Busy Bob", slack.messages[0]["recipient"])
        self.assertEqual("Warning: You currently have 5 jira issues in progress. That's too many. Here's a list: XXX-1, XXX-2, XXX-3, XXX-4, XXX-5",
                         slack.messages[0]["message"])