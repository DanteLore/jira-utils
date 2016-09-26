class JiraChart:
    ctm_dark_blue = "#12468B"
    ctm_light_blue = "#86A6DE"
    ctm_green = "#3DB633"

    def __init__(self, x_data, title=None, y_tick_count=8):
        self.y_tick_count = y_tick_count
        self.title = title
        self.x_data = x_data

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