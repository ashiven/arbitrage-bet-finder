from parsers import *
from collections import defaultdict


class ArbitrageService:
    def __init__(self):
        self.parsers = dict()
        self.matches = defaultdict(list)
        self.arbitrages = dict()

    def add_parser(self, parser, name):
        parser.get_matches()
        self.parsers[name] = parser

    def accumulate_matches(self):
        for name, parser in self.parsers.items():
            for match, odds in parser.matches.items():
                self.matches[match].append([odds, name])

    def find_arbitrages(self):
        pass
        # self.arbitrages
