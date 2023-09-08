from parsers import *
from collections import defaultdict


class ArbitrageService:
    def __init__(self):
        self.parsers = dict()
        self.matches = defaultdict(list)
        self.arbitrages = dict()

    def add_parser(self, parser, name):
        self.parsers[name] = parser

    def accumulate_matches(self):
        for parser in self.parsers.values():
            if not parser.matches:
                parser.get_matches()

        for name, parser in self.parsers.items():
            for match, odds in parser.matches.items():
                self.matches[match].append([odds, name])

        print("Overview over all accumulated matches and their odds:\n")
        print(dict(self.matches))

    def find_arbitrages(self):
        pass
        # self.arbitrages
