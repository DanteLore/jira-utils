import math

import matplotlib
import numpy as np

from charts.jira_chart import JiraChart

matplotlib.use('Agg')
from matplotlib import pyplot as plt


class BarChart(JiraChart):

    def __init__(self, x_data, y_data, title=None, y_tick_count=8):
        JiraChart.__init__(self, x_data, title, y_tick_count)

        self.y_data = y_data

    def save_to_file(self, filename):
        fig, ax = plt.subplots(facecolor="white", figsize=(10, 4))

        width = .9
        ind = np.arange(len(self.y_data))
        plt.bar(ind, self.y_data, width=width, linewidth=0, facecolor=self.ctm_green)
        plt.xticks(ind + width / 2, self.x_data)

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(True)
        ax.spines['left'].set_visible(True)

        ax.xaxis.set_ticks_position('none')
        ax.yaxis.set_ticks_position('left')
        ticks = math.ceil(max(self.y_data) / self.y_tick_count) + 1
        plt.yticks(np.arange(0, max(self.y_data) + 1, ticks))

        self.set_background_color(ax, "white")
        self.set_foreground_color(ax, self.ctm_dark_blue)
        fig.patch.set_facecolor("white")

        if self.title:
            plt.title(self.title)

        if len(self.x_data) > 8:
            fig.autofmt_xdate()
        fig.set_tight_layout(True)

        plt.savefig(filename, facecolor=fig.get_facecolor(), edgecolor='none', transparent=True)


