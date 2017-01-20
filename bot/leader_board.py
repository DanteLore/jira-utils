from itertools import groupby


class LeaderBoard:
    def __init__(self, jira, slack):
        self.jira = jira
        self.slack = slack

    digits = {
        1: ":one:",
        2: ":two:",
        3: ":three:",
        4: ":four:",
        5: ":five:",
        6: ":six:",
        7: ":seven:",
        8: ":eight:",
        9: ":nine:"
    }

    def format_user_mention(self, user_name):
        user_id = self.slack.search_user_id(user_name)
        if user_id:
            user = "<@{0}>".format(user_id)
        else:
            user = "*{0}*".format(user_name)
        return user

    def group_issues(self, issues):
        def get_key(card):
            return str(card.fields.assignee)

        # You must SORT before you GROUP. Which is :poo:
        issues = sorted(list(issues), key=get_key)

        for name, cards in groupby(issues, key=get_key):
            yield (name, len(list(cards)))

    def format_table(self, title, issues):
        groups = sorted(self.group_issues(issues), key=lambda i: i[1], reverse=True)

        if len(groups) == 0:
            return "No leaderboard to show, as no 'Done' issues found! :cry:"

        lines = [title]
        i = 0
        for (name, count) in groups:
            i += 1
            if i <= 5:
                lines.append("{0} {1} ({2} issues)".format(self.digits[i], self.format_user_mention(name), count))
            else:
                break

        return "\n".join(lines)

    def last_week(self):
        issues = self.jira.resolved_last_week().status_is("Done").get_issues()
        return self.format_table("Last week's leaderboard looked like this:", issues)

    def this_week(self):
        issues = self.jira.resolved_this_week().status_is("Done").get_issues()
        return self.format_table("Leaderboard for this week:", issues)