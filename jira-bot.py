import argparse
import logging.handlers
from datetime import datetime
from time import sleep

from bot.jirabot import JiraBot
from bot.slack import Slack
from jira_utils.jira_utils import Jira

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Jira Bot')
    parser.add_argument('--jira', help='Jira Server', required=True)
    parser.add_argument('--project', help='Jira Project ID', required=True)
    parser.add_argument('--label', help='Jira Label', default=None)
    parser.add_argument('--freq', help='Polling frequency in minutes (default 30)', default=30)
    parser.add_argument('--wake-hour', help='Hour of day to wake up (default 6)', default=6)
    parser.add_argument('--sleep-hour', help='Hour of day to sleep (default 19)', default=19)
    parser.add_argument('--fix-version', help='Jira Fix Version', default=None)
    parser.add_argument('--wip-limit', help='How many In Progress issues is too many?', default="3")
    parser.add_argument('--slack-key', help='The key for slack', required=True)
    parser.add_argument('--user', help='Jira username', required=True)
    parser.add_argument('--channel', help='The channel on which to complain about stuff', required=True)
    parser.add_argument('--forever', help='Use this switch to run the script forever (once ever 5 mins)',
                        action='store_true', default=False)
    parser.add_argument('--log-level', help='Log level to use. Default=INFO', default="INFO")

    args = parser.parse_args()

    logger = logging.getLogger("JiraBot")
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    file_handler = logging.handlers.RotatingFileHandler("/var/log/jirabot/jirabot.log", maxBytes=10485760, backupCount=10)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.setLevel(args.log_level)
    logger.addHandler(stream_handler)

    jira = Jira(args.jira, args.user, logger=logger)
    slack = Slack(args.slack_key, logger=logger)

    bot = JiraBot(jira=jira,
                  slack=slack,
                  project=args.project,
                  label=args.label,
                  fix_version=args.fix_version,
                  channel=args.channel,
                  logger=logger,
                  wip_limit=args.wip_limit)

    slack.send(args.channel, ":tada: I just restarted. Hello!")
    count = 0
    while True:
        try:
            bot.process_messages()
            hour = datetime.now().hour
            if count > (args.freq * 60 * 10) and args.wake_hour <= hour < args.sleep_hour:
                count = 0
                bot.send_periodic_update()
            count += 1
        except Exception as e:
            logger.exception(e)
            logger.error(e.message)
        if not args.forever:
            break
        sleep(0.1)
