from service import ArbitrageService
from parsers import ggBetParser, ThunderPickParser


def main():
    AS = ArbitrageService()

    ## initialize parsers
    gg = ggBetParser()
    tp = ThunderPickParser()

    ## add parsers to service
    AS.add_parser(gg, "gg.bet")
    AS.add_parser(tp, "thunderpick.io")

    AS.accumulate_matches()
    print(dict(AS.matches))


if __name__ == "__main__":
    main()
