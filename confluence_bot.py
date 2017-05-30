import argparse
import logging.handlers
from datetime import datetime, timedelta

import pytz
from dateutil import parser
from dateutil.tz import tzutc

from confluence.confluence import Confluence
from confluence.kanban_report import KanbanReport
from confluence.metrics_report import MetricsReport
from jira_utils.jira_utils import Jira

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--user", required=True, help="Your confluence username")
    argparser.add_argument("--confluence", required=True, help="Confluence (and Jira) base URL e.g. https://xxx.atlassian.net")
    argparser.add_argument("--pageid", required=True, type=int, help="Page ID")
    argparser.add_argument("--jql", default=None, help="Base JQL fragment")
    argparser.add_argument("--title", default="Untitled", help="Title of the page")
    argparser.add_argument("--start", default=None, help="Start date (YYYY/MM/DD)")
    argparser.add_argument("--end", default=None, help="End date (YYYY/MM/DD) optional")
    argparser.add_argument("--report", required=True, help="Report to run [kanban, metrics]")
    args = argparser.parse_args()

    logger = logging.getLogger("ConfluenceBot")
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    file_handler = logging.handlers.RotatingFileHandler("/var/log/confluencebot/confluencebot.log", maxBytes=10485760, backupCount=10)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.setLevel("INFO")
    logger.addHandler(stream_handler)

    jira_server = args.confluence.strip("/").replace("http://", "")
    confluence_base_url = args.confluence.strip("/") + "/wiki/rest/api/content"

    jira = Jira(jira_server, username=args.user, jql=args.jql, logger=logger)
    confluence = Confluence(base_url=confluence_base_url, username=args.user)

    # Lest we forget...
    # content = confluence.get_page_body(args.pageid)
    # content = content.replace("thingies", "thingies thingies")
    # confluence.update_page(args.pageid, content)
    # print confluence.get_page_body(args.pageid)

    if args.start:
        start = pytz.utc.localize(parser.parse(args.start))
    else:
        start = pytz.utc.localize(datetime.utcnow()) - timedelta(days=7)

    if args.end:
        end = pytz.utc.localize(parser.parse(args.end))
    else:
        end = pytz.utc.localize(datetime.utcnow())

    if args.report == "kanban":
        report = KanbanReport(jira, logger, args.title, start, end)
        confluence.create_page(args.pageid, *report.generate())
    elif args.report == "metrics":
        report = MetricsReport(jira, logger, args.title, start, end)
        confluence.update_page(args.pageid, *report.generate())
    elif args.report == "weekly_kanban":
        week_start = start - timedelta(days=start.weekday())
        report_end = end - timedelta(days=end.weekday())
        year_start = week_start - timedelta(weeks=52)

        main_page = MetricsReport(jira, logger, args.title, year_start, report_end)
        confluence.update_page(args.pageid, *main_page.generate())
        detail = KanbanReport(jira, logger, args.title, week_start, report_end)
        confluence.create_page(args.pageid, *detail.generate())
    else:
        print "No such report {0}".format(args.report)
