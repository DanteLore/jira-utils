import argparse
import logging.handlers
from datetime import datetime

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
    argparser.add_argument("--start", required=True, help="Start date (YYYY/MM/DD)")
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

    jira = Jira(jira_server, jql=args.jql, logger=logger)
    confluence = Confluence(base_url=confluence_base_url, username=args.user)

    # Lest we forget...
    # content = confluence.get_page_body(args.pageid)
    # content = content.replace("thingies", "thingies thingies")
    # confluence.update_page(args.pageid, content)
    # print confluence.get_page_body(args.pageid)

    start = pytz.utc.localize(parser.parse(args.start))

    if args.end:
        end = pytz.utc.localize(parser.parse(args.end))
    else:
        end = None

    if args.report == "kanban":
        report = KanbanReport(jira, args.title, start, end)
        confluence.create_page(args.pageid, *report.generate())
    elif args.report == "metrics":
        report = MetricsReport(jira, args.title, start, end)
        confluence.create_page(args.pageid, *report.generate())
    else:
        print "No such report {0}".format(args.report)
