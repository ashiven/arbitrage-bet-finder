from arbitrage.service import ArbitrageService
from arbitrage.parsers import BCGameParser, ThunderPickParser
from arbitrage.bettype import BetType


def main():
    AS = ArbitrageService(variant=BetType.CS, verbose=False)

    ## initialize parsers (the SOCCER variant does not work yet on parsers)
    bc = BCGameParser()
    tp = ThunderPickParser()

    ## add parsers to service
    AS.add_parser(bc)
    AS.add_parser(tp)

    ## get the latest matches and their odds for every website
    AS.accumulate_matches()

    ## find out if there are any arbitrages across the sites
    AS.find_arbitrages()


if __name__ == "__main__":
    main()
