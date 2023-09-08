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

    AS.accumulate_matches()


if __name__ == "__main__":
    main()
