from service import ArbitrageService
from parsers import BCGameParser, ThunderPickParser
from bettype import BetType


def main():
    AS = ArbitrageService()

    ## initialize parsers
    bc = BCGameParser(variant=BetType.SOCCER, verbose=False)
    tp = ThunderPickParser(variant=BetType.SOCCER, verbose=False)

    ## add parsers to service
    AS.add_parser(bc)
    AS.add_parser(tp)

    ## get the latest matches and their odds for every service
    AS.accumulate_matches()

    ## find out if there are any arbitrages across the sites
    AS.find_arbitrages()


if __name__ == "__main__":
    main()
