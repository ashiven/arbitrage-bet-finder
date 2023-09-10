from arbitrage.parsers import *
from collections import defaultdict


class ArbitrageService:
    def __init__(self, retries=3, variant=BetType.CS, verbose=False):
        self.parsers = dict()
        self.matches = defaultdict(list)
        self.arbitrages = dict()
        self.retries = retries
        self.variant = variant
        self.verbose = verbose

    def add_parser(self, parser):
        parser.configure(self.retries, self.variant, self.verbose)
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
        found = False
        for match, odds in self.matches.items():
            max_one = max(odds, key=lambda x: x[0][0])
            max_two = max(odds, key=lambda x: x[0][1])
            if max_one[0][0] == -1 or max_two[0][1] == -1:
                continue

            # calculate whether an arbitrage exists
            arbitrage = 1 / max_one[0][0] + 1 / max_two[0][1]
            if self.verbose:
                print(
                    f"{match[0]} VS {match[1]}\n - highest odds: {max_one[0][0]}  {max_two[0][1]}\n - probability:  {arbitrage*100:.2f}%\n"
                )
            if arbitrage < 1:
                found = True
                self.arbitrages[match] = [
                    max_one[1],
                    max_two[1],
                    max_one[0][0],
                    max_two[0][1],
                    f"{arbitrage*100:.2f}%",
                ]
                print(f"----{match[0]} VS {match[1]}----\n")
                print(
                    f"[!] Found an arbitrage between {max_one[1]} and {max_two[1]} with a probability of {arbitrage*100:.2f}%\n"
                )
                WINNINGS = 100
                odd_one = max_one[0][0]
                odd_two = max_two[0][1]
                bet_one = WINNINGS / odd_one
                bet_two = WINNINGS / odd_two
                print(
                    f"[+] Suggested arbitrage bet (non-biased): {bet_one}$ on {match[0]} and {bet_two}$ on {match[1]} for a profit of {WINNINGS - bet_one+bet_two}$\n"
                )
                print(f"[+] Suggested arbitrage bet (biased): ")
                # TODO:
                # 1) figure out biased arbitrage formula
                # 2) enter found arbitrages in a decent format into self.arbitrages
                # 3) create a show_arbitrages() function similar to show_matches()

        if not found:
            print("Could not find any arbitrages :(")
