import unittest

from bot.random_quote import RandomQuote


class RandomQuoteTests(unittest.TestCase):
    def setUp(self):
        self.quotes = RandomQuote()

    def test_some_quotes(self):
        for i in range(1, 10):
            print "{0}: {1}".format(i, self.quotes.get_quote())
