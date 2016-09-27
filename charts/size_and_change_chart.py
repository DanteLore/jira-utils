import numpy as np
from matplotlib import pyplot as plt

from charts.jira_chart import JiraChart


class SizeAndChangeChart(JiraChart):
    def __init__(self, x_data, positive_data, negative_data, size_data, title=None, y_tick_count=8):
        JiraChart.__init__(self, x_data, title, y_tick_count)
        self.size_data = size_data
        self.negative_data = negative_data
        self.positive_data = positive_data

    def save_to_file(self, filename):
        fig, ax1 = plt.subplots(facecolor="white", figsize=(16, 6))

        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(True)
        ax1.spines['bottom'].set_visible(True)
        ax1.spines['left'].set_visible(True)
        ax1.xaxis.set_ticks_position('none')
        ax1.yaxis.set_ticks_position('left')
        self.set_background_color(ax1, "white")
        self.set_foreground_color(ax1, self.ctm_dark_blue)

        ax2 = ax1.twinx()
        self.set_background_color(ax2, "white")
        self.set_foreground_color(ax2, self.ctm_dark_blue)
        fig.patch.set_facecolor("white")

        if self.title:
            plt.title(self.title)

        width = .9
        ind = np.arange(len(self.negative_data))
        ax1.bar(ind, self.negative_data, width=width, linewidth=0, facecolor="#CC0000")
        plt.xticks(ind + width / 2, self.x_data)

        ax1.bar(ind, self.positive_data, width=width, linewidth=0, facecolor=self.ctm_green)
        ax1.set_ylim([min(self.negative_data) - 1, max(self.positive_data) + 1])

        plt.xticks(ind + width / 2, self.x_data)
        ax2.plot(ax1.get_xticks(), self.size_data, linestyle='-', linewidth=4.0, color=self.ctm_light_blue)
        ax2.set_ylim([0, max(self.size_data) + 5])

        if len(self.x_data) > 8:
            fig.autofmt_xdate()
        fig.set_tight_layout(True)
        plt.savefig(filename, facecolor=fig.get_facecolor(), edgecolor='none', transparent=True)