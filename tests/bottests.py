import logging
import unittest

from freezegun import freeze_time

from bot.jirabot import JiraBot
from bot.message_to_jira_attachment_converter import MessageToJiraAttachmentConverter
from tests.mock_jira import MockJira
from tests.mock_slack import MockSlack


class JiraBotTests(unittest.TestCase):
    def setUp(self):
        self.logger = logging.getLogger("JiraBot")
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
        self.logger.setLevel("DEBUG")
        self.logger.addHandler(stream_handler)

    def test_messages_when_nothing_interesting_happening(self):
        jira = MockJira(issues=[
            {"id": "XXX-1", "summary": "My first Jira", "status": "Backlog"},
            {"id": "XXX-2", "summary": "My second Jira", "status": "Backlog"},
        ])
        slack = MockSlack()
        bot = JiraBot(jira, slack, "XXX", "LABEL", 3, logger=self.logger)
        bot.send_periodic_update()
        self.assertEqual(len(slack.outgoing_messages), 2)
        self.assertEqual(":partyparrot:", slack.outgoing_messages[1]["message"])

    def test_message_sent_if_issue_assigned_but_not_in_progress(self):
        jira = MockJira(issues=[
            {"id": "XXX-1", "summary": "My first Jira", "assignee": "Fred Bloggs", "status": "Backlog"},
            {"id": "XXX-2", "summary": "My second Jira", "assignee": "None", "status": "Backlog"},
            {"id": "XXX-3", "summary": "My third Jira", "assignee": "Fred Jones", "status": "In Progress"},
        ])
        slack = MockSlack()
        bot = JiraBot(jira, slack, "XXX", "LABEL", "#channel_name", 3, logger=self.logger)
        bot.send_periodic_update()
        self.assertEqual(len(slack.outgoing_messages), 1)
        self.assertEqual("#channel_name", slack.outgoing_messages[0]["recipient"])
        self.assertEqual(':warning: XXX-1 is assigned to *Fred Bloggs* but still in the Backlog state',
                         slack.outgoing_messages[0]["message"])

    def test_message_sent_if_issue_in_progress_but_not_assigned(self):
        jira = MockJira(issues=[
            {"id": "XXX-1", "summary": "My first Jira", "assignee": "Cheesy Phil", "status": "In Progress"},
            {"id": "XXX-2", "summary": "My second Jira", "assignee": "None", "status": "In Progress"},
            {"id": "XXX-3", "summary": "My third Jira", "assignee": "Fred Jones", "status": "In Progress"},
        ])
        slack = MockSlack()
        bot = JiraBot(jira, slack, "XXX", "LABEL", "#the_channel", logger=self.logger)
        bot.send_periodic_update()
        self.assertEqual(1, len(slack.outgoing_messages))
        self.assertEqual("#the_channel", slack.outgoing_messages[0]["recipient"])
        self.assertEqual(":warning: XXX-2 is marked as In Progress but not assigned to anyone",
                         slack.outgoing_messages[0]["message"])

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
        bot = JiraBot(jira, slack, "XXX", "LABEL", "#chan1", 3, logger=self.logger)
        bot.send_periodic_update()
        self.assertEqual(len(slack.outgoing_messages), 1)
        self.assertEqual("#chan1", slack.outgoing_messages[0]["recipient"])
        self.assertEqual(
            ":warning: *Busy Bob* currently has 5 jira issues in progress. That's too many. Here's a list: XXX-1, XXX-2, XXX-3, XXX-4, XXX-5",
            slack.outgoing_messages[0]["message"])

    @freeze_time("2016-08-10 09:00:00")
    def test_new_issues_in_backlog_notified_on_channel(self):
        jira = MockJira(issues=[
            {"id": "AAA-2", "summary": "I am new", "status": "Backlog", "created": u'2016-08-10T07:55:00.000+0100'},
            {"id": "AAA-1", "summary": "I am not new", "status": "Backlog", "created": u'2016-08-08T14:50:36.000+0100'}
        ])
        slack = MockSlack()
        bot = JiraBot(jira, slack, "AAA", "LABEL", "#whatever", logger=self.logger)
        bot.send_periodic_update()
        self.assertEqual(3, len(slack.outgoing_messages))
        self.assertEqual("There are no warnings. It's all good!", slack.outgoing_messages[0]["message"])
        self.assertEqual(':partyparrot:', slack.outgoing_messages[1]["message"])
        self.assertEqual(':memo: New issue AAA-2 added', slack.outgoing_messages[2]["message"])

    @freeze_time("2016-08-10 09:00:00")
    def test_multiple_new_issues_in_backlog_notified_on_channel(self):
        jira = MockJira(issues=[
            {"id": "AAA-3", "summary": "I am also new", "status": "Backlog", "created": u'2016-08-10T07:58:00.000+0100'},
            {"id": "AAA-2", "summary": "I am new", "status": "Backlog", "created": u'2016-08-10T07:55:00.000+0100'},
            {"id": "AAA-1", "summary": "I am not new", "status": "Backlog", "created": u'2016-08-08T14:50:36.000+0100'}
        ])
        slack = MockSlack()
        bot = JiraBot(jira, slack, "AAA", "LABEL", "#whatever", logger=self.logger)
        bot.send_periodic_update()
        self.assertEqual(4, len(slack.outgoing_messages))
        self.assertEqual("There are no warnings. It's all good!", slack.outgoing_messages[0]["message"])
        self.assertEqual(':partyparrot:', slack.outgoing_messages[1]["message"])
        self.assertEqual(':memo: New issue AAA-3 added', slack.outgoing_messages[2]["message"])
        self.assertEqual(':memo: New issue AAA-2 added', slack.outgoing_messages[3]["message"])

    @freeze_time("2016-08-10 09:00:00")
    def test_new_issues_not_repeated_in_channel(self):
        jira = MockJira(issues=[
            {"id": "AAA-2", "summary": "I am new", "status": "Backlog", "created": u'2016-08-10T07:55:00.000+0100'},
            {"id": "AAA-1", "summary": "I am not new", "status": "Backlog", "created": u'2016-08-08T14:50:36.000+0100'}
        ])
        slack = MockSlack()
        bot = JiraBot(jira, slack, "AAA", "LABEL", "#things", logger=self.logger)
        bot.send_periodic_update()
        bot.send_periodic_update()
        self.assertEqual(3, len(slack.outgoing_messages))

    @freeze_time("2016-08-10 09:00:00")
    def test_in_progress_for_too_long(self):
        # Note that the mock Jira uses Created Date for filtering - since it doesn't have state change knowledge
        # We're testing that the correct number of days is passed and that the messages are created, not the JQL itself.
        jira = MockJira(issues=[
            {"id": "AAA-3", "assignee": "Bad Gary", "summary": "I'm new too", "status": "In Progress", "created": u'2016-08-10T07:58:00.000+0100'},
            {"id": "AAA-2", "assignee": "Bad Gary", "summary": "I am new-ish", "status": "In Progress", "created": u'2016-08-07T07:55:00.000+0100'},
            {"id": "AAA-1", "assignee": "Bad Gary", "summary": "I've been in progress for ages!", "status": "In Progress", "created": u'2016-08-01T14:50:36.000+0100'}
        ])
        slack = MockSlack()
        bot = JiraBot(jira, slack, "AAA", "LABEL", "#whatever", logger=self.logger, wip_limit=10, wip_time_limit=7)
        bot.send_periodic_update()
        self.assertEqual(1, len(slack.outgoing_messages))
        self.assertEqual("#whatever", slack.outgoing_messages[0]["recipient"])
        self.assertEqual(":clock2: AAA-1 has been in progress for longer than 7 days. Is it blocked, *Bad Gary*?",
                         slack.outgoing_messages[0]["message"])

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

    def get_test_issue_set(self):
        return [
            {"id": "XXX-1", "summary": "My first Jira", "assignee": "Cheesy Phil", "status": "In Progress", "created": u'2016-08-08T14:50:36.000+0100'},
            {"id": "XXX-2", "summary": "My second Jira", "assignee": "Fred Jones", "status": "In Progress", "created": u'2016-08-08T14:50:36.000+0100'},
            {"id": "XXX-3", "summary": "My third Jira", "assignee": None, "status": "To Do", "created": u'2016-08-10T07:55:00.000+0100'},
            {"id": "XXX-4", "summary": "My fourth Jira", "assignee": None, "status": "Done", "created": u'2016-08-08T14:50:36.000+0100'},
            {"id": "XXX-5", "summary": "My fifth Jira", "assignee": None, "status": "Backlog", "created": u'2016-08-08T14:50:36.000+0100'},
            {"id": "XXX-6", "summary": "My sixth Jira", "assignee": None, "status": "Backlog", "created": u'2016-08-10T07:55:00.000+0100'},
            {"id": "XXX-7", "summary": "My seventh Jira", "assignee": "Donald Trump", "status": "Backlog", "created": u'2016-08-08T14:50:36.000+0100'}
        ]

    def test_unknown_command(self):
        jira = MockJira(issues=[])
        slack = MockSlack()
        bot = JiraBot(jira, slack, "AAA", "LABEL", "#things", logger=self.logger)
        slack.add_incoming({u'text': u'<@BOTID> herrings are obfuscation cheese', u'user': u'USER_ID'})
        bot.process_messages()
        self.assertEqual(1, len(slack.outgoing_messages))
        self.assertTrue("<@USER_ID>" in slack.outgoing_messages[0]["message"])

    @freeze_time("2016-08-10 09:00:00")
    def test_request_to_show_everything(self):
        jira = MockJira(issues=self.get_test_issue_set())
        slack = MockSlack()
        bot = JiraBot(jira, slack, "AAA", "LABEL", "#things", logger=self.logger)
        slack.add_incoming({u'text': u'<@BOTID> show warnings'})
        bot.process_messages()
        self.assertEqual(1, len(slack.outgoing_messages))

    @freeze_time("2016-08-10 09:00:00")
    def test_request_to_show_everything_after_sending_update(self):
        jira = MockJira(issues=self.get_test_issue_set())
        slack = MockSlack()
        bot = JiraBot(jira, slack, "AAA", "LABEL", "#things", logger=self.logger)
        bot.send_periodic_update()
        self.assertEqual(3, len(slack.outgoing_messages))
        slack.add_incoming({u'text': u'<@BOTID> show errors'})
        bot.process_messages()
        self.assertEqual(4, len(slack.outgoing_messages))

    @freeze_time("2016-08-10 09:00:00")
    def test_request_to_show_new_issues(self):
        jira = MockJira(issues=self.get_test_issue_set())
        slack = MockSlack()
        bot = JiraBot(jira, slack, "AAA", "LABEL", "#things", logger=self.logger)
        slack.add_incoming({u'text': u'<@BOTID> show new issues'})
        bot.process_messages()
        self.assertEqual(1, len(slack.outgoing_messages))
        self.assertTrue("XXX-6" in slack.outgoing_messages[0]["message"])
        self.assertTrue("XXX-3" in slack.outgoing_messages[0]["message"])

    @freeze_time("2016-08-10 09:00:00")
    def test_request_to_show_in_progress(self):
        jira = MockJira(issues=self.get_test_issue_set())
        slack = MockSlack()
        bot = JiraBot(jira, slack, "AAA", "LABEL", "#things", logger=self.logger)
        slack.add_incoming({u'text': u'<@BOTID> show in progress'})
        bot.process_messages()
        self.assertEqual(1, len(slack.outgoing_messages))
        self.assertTrue("XXX-1" in slack.outgoing_messages[0]["message"])
        self.assertTrue("XXX-2" in slack.outgoing_messages[0]["message"])

    @freeze_time("2016-08-10 09:00:00")
    def test_request_to_show_to_do(self):
        jira = MockJira(issues=self.get_test_issue_set())
        slack = MockSlack()
        bot = JiraBot(jira, slack, "AAA", "LABEL", "#things", logger=self.logger)
        slack.add_incoming({u'text': u'<@BOTID> show to do'})
        bot.process_messages()
        self.assertEqual(1, len(slack.outgoing_messages))
        self.assertTrue("XXX-3" in slack.outgoing_messages[0]["message"])

    @freeze_time("2016-08-10 09:00:00")
    def test_request_to_show_backlog(self):
        jira = MockJira(issues=self.get_test_issue_set())
        slack = MockSlack()
        bot = JiraBot(jira, slack, "AAA", "LABEL", "#things", logger=self.logger)
        slack.add_incoming({u'text': u'<@BOTID> show backlog'})
        bot.process_messages()
        self.assertEqual(1, len(slack.outgoing_messages))
        self.assertTrue("XXX-7" in slack.outgoing_messages[0]["message"])

    @freeze_time("2016-08-10 09:00:00")
    def test_request_status_summary(self):
        jira = MockJira(issues=self.get_test_issue_set())
        slack = MockSlack()
        bot = JiraBot(jira, slack, "AAA", "LABEL", "#things", logger=self.logger)
        slack.add_incoming({u'text': u'<@BOTID> status summary'})
        bot.process_messages()
        self.assertEqual(1, len(slack.outgoing_messages))
        msg = slack.outgoing_messages[0]["message"].lower()
        self.assertTrue("backlog: *3*" in msg)
        self.assertTrue("to do: *1*" in msg)
        self.assertTrue("in progress: *2*" in msg)

    def test_name_lookups_for_mentions(self):
        jira = MockJira(issues=[
            {"id": "XXX-1", "summary": "My first Jira", "assignee": "Fred Bloggs", "status": "Backlog"}
        ])
        slack = MockSlack(name_lookup={"Fred Bloggs": "BLOGGSID"})
        bot = JiraBot(jira, slack, "XXX", "LABEL", "#channel_name", 3, logger=self.logger)
        bot.send_periodic_update()
        self.assertEqual(len(slack.outgoing_messages), 1)
        self.assertEqual("#channel_name", slack.outgoing_messages[0]["recipient"])
        self.assertEqual(':warning: XXX-1 is assigned to <@BLOGGSID> but still in the Backlog state',
                         slack.outgoing_messages[0]["message"])
