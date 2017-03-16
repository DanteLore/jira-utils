import argparse
import logging.handlers
from datetime import datetime

from dateutil.tz import tzutc

from confluence.confluence import Confluence
from confluence.kanban_report import KanbanReport
from jira_utils.jira_utils import Jira

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", help="Your confluence username")
    parser.add_argument("--confluence", help="Confluence (and Jira) base URL e.g. https://xxx.atlassian.net")
    parser.add_argument("--pageid", type=int, help="Parent page ID")
    parser.add_argument("--jql", default=None, help="Base JQL fragment")
    parser.add_argument("--title", default="Untitled", help="Title of the page")
    args = parser.parse_args()

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

    start = datetime(2017, 02, 27, tzinfo=tzutc())

    kbr = KanbanReport(jira, args.title, start)
    page_title, page_body = kbr.generate()
    confluence.create_page(args.pageid, page_body, page_title)
