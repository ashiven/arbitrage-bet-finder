from parsers import *
from collections import defaultdict


class ArbitrageService:
    def __init__(self):
        self.parsers = dict()
        self.matches = defaultdict(list)
        self.arbitrages = dict()

    def add_parser(self, parser):
        self.parsers[parser.website] = parser

    def show_matches(self):
        print("\n")
        for match, odds in self.matches.items():
            print(f"----{match[0]} VS {match[1]}----\n")
            for odd, website in odds:
                print("{:<15}  {:<4}  {:<4}".format(website, odd[0], odd[1]))
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
        for match, odds in self.matches.items():
            max_one = max(odds, key=lambda x: x[0][0])
            max_two = max(odds, key=lambda x: x[0][1])
            if max_one[0][0] == "TBA" or max_two[0][1] == "TBA":
                continue

            # calculate whether an arbitrage exists
            arbitrage = 1 / max_one[0][0] + 1 / max_two[0][1]
            found = False
            if arbitrage < 1:
                found = True
                print(f"----{match[0]} VS {match[1]}----\n")
                print(
                    f"[!] Found an arbitrage between {max_one[1]} and {max_two[1]} with a percent of {arbitrage*100:.2f}%\n"
                )

        if not found:
            print("Could not find any arbitrages :(")
