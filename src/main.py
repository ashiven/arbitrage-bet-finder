from service import ArbitrageService
from parsers import ggBetParser


def main():
    AS = ArbitrageService()

    ## initialize parsers
    gg = ggBetParser()

    ## add parsers to service
    AS.add_parser(gg)


if __name__ == "__main__":
    main()
