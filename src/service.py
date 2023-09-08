from parsers import *
from collections import defaultdict


class ArbitrageService:
    def __init__(self):
        self.parsers = dict()
        self.matches = defaultdict(list)
        self.arbitrages = dict()

    def add_parser(self, parser, name):
        self.parsers[name] = parser

    def show_matches(self):
        for match, odds in self.matches.items():
            print(f"----{match[0]} VS {match[1]}----\n")
            for odd, website in odds:
                print(f"{website}:  {odd[0]}  {odd[1]}")
            print("\n")

    def accumulate_matches(self):
        print("Accumulating match data... Please wait.")
        for parser in self.parsers.values():
            if not parser.matches:
                parser.get_matches()

        for name, parser in self.parsers.items():
            for match, odds in parser.matches.items():
                self.matches[match].append([odds, name])

        self.show_matches()

    def find_arbitrages(self):
        pass
        # self.arbitrages
