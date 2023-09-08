from service import ArbitrageService
from parsers import BCGameParser, ThunderPickParser


def main():
    AS = ArbitrageService()

    ## initialize parsers
    bc = BCGameParser()
    tp = ThunderPickParser()

    ## add parsers to service
    AS.add_parser(bc, "bc.game")
    AS.add_parser(tp, "thunderpick.io")

    ## get the latest matches and their odds for every service
    AS.accumulate_matches()

    ## find out if there are any arbitrages across the sites
    AS.find_arbitrages()


if __name__ == "__main__":
    main()
