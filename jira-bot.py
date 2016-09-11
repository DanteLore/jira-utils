import argparse
import logging
from time import sleep

from bot.jirabot import MessageToJiraAttachmentConverter, JiraBot
from bot.slack import Slack
from jira_utils.jira_utils import Jira

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Jira Bot')
    parser.add_argument('--jira', help='Jira Server', required=True)
    parser.add_argument('--project', help='Jira Project ID', required=True)
    parser.add_argument('--label', help='Jira Label', required=True)
    parser.add_argument('--wip-limit', help='How many In Progress issues is too many?', default="3")
    parser.add_argument('--slack-key', help='The key for slack', required=True)
    parser.add_argument('--channel', help='The channel on which to complain about stuff', required=True)
    parser.add_argument('--forever', help='Use this switch to run the script forever (once ever 5 mins)',
                        action='store_true', default=False)
    parser.add_argument('--log-level', help='Log level to use. Default=INFO', default="INFO")

    args = parser.parse_args()

    logger = logging.getLogger("JiraBot")
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    logger.setLevel(args.log_level)
    logger.addHandler(stream_handler)

    jira = Jira(args.jira)
    attachment_converter = MessageToJiraAttachmentConverter(jira)
    slack = Slack(args.slack_key, attachment_converter, logger)

    bot = JiraBot(jira=jira,
                  slack=slack,
                  project=args.project,
                  label=args.label,
                  channel=args.channel,
                  logger=logger,
                  wip_limit=args.wip_limit)

    count = 0
    while True:
        try:
            bot.process_messages()
            if count > 3000:
                count = 0
                bot.send_periodic_update()
            count += 1
        except Exception as e:
            logger.exception(e)
            logger.error(e.message)
            slack.send("dan_taylor", "I crashed!!")
            slack.send("dan_taylor", e.message)
        if not args.forever:
            break
        sleep(0.1)
