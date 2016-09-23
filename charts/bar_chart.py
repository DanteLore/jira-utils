import matplotlib
import numpy as np
matplotlib.use('Agg')
from matplotlib import pyplot as plt


class BarChart:
    ctm_dark_blue = "#12468B"
    ctm_light_blue = "#86A6DE"
    ctm_green = "#3DB633"

    def __init__(self, x_data, y_data, title=None):
        self.title = title
        self.x_data = x_data
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
        plt.yticks(np.arange(min(self.y_data), max(self.y_data)+1, 1.0))

        self.set_background_color(ax, "white")
        self.set_foreground_color(ax, self.ctm_dark_blue)
        fig.patch.set_facecolor("white")

        if self.title:
            plt.title(self.title)

        # fig.autofmt_xdate()
        fig.set_tight_layout(True)

        plt.savefig(filename, facecolor=fig.get_facecolor(), edgecolor='none', transparent=True)

    def set_foreground_color(self, ax, color):
        """For the specified axes, sets the color of the frame, major ticks,
            tick labels, axis labels, title and legend
        """
        for tl in ax.get_xticklines() + ax.get_yticklines():
            tl.set_color(color)
        for spine in ax.spines:
            ax.spines[spine].set_edgecolor(color)
        for tick in ax.xaxis.get_major_ticks():
            tick.label1.set_color(color)
        for tick in ax.yaxis.get_major_ticks():
            tick.label1.set_color(color)
        ax.axes.xaxis.label.set_color(color)
        ax.axes.yaxis.label.set_color(color)
        ax.axes.xaxis.get_offset_text().set_color(color)
        ax.axes.yaxis.get_offset_text().set_color(color)
        ax.axes.title.set_color(color)
        lh = ax.get_legend()
        if lh is not None:
            lh.get_title().set_color(color)
            lh.legendPatch.set_edgecolor('none')
            labels = lh.get_texts()
            for lab in labels:
                lab.set_color(color)
        for tl in ax.get_xticklabels():
            tl.set_color(color)
        for tl in ax.get_yticklabels():
            tl.set_color(color)

    def set_background_color(self, ax, color):
        """Sets the background color of the current axes (and legend).
            Use 'None' (with quotes) for transparent. To get transparent
            background on saved figures, use:
            pp.savefig("fig1.svg", transparent=True)
        """
        ax.patch.set_facecolor(color)
        lh = ax.get_legend()
        if lh is not None:
            lh.legendPatch.set_facecolor(color)