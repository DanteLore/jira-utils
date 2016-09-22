import unittest
import webbrowser

from charts.bar_chart import BarChart


class ChartTests(unittest.TestCase):
    def test_bar_chart(self):
        x_data = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        y_data = [3, 2, 1, 2, 3]

        chart = BarChart(x_data, y_data)
        chart.save_to_file("/tmp/chart1.png")

        webbrowser.open("file:///tmp/chart1.png")
