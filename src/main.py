from arbitrage.service import ArbitrageService
from arbitrage.parsers import (
    BCGameParser,
    ThunderPickParser,
    RivalryParser,
    BetsIOParser,
)
from arbitrage.bettype import BetType


def main():
    # (the SOCCER variant does not work yet)
    AS = ArbitrageService(variant=BetType.CS, verbose=True, retries=5)

    ## initialize parsers
    bc = BCGameParser()
    tp = ThunderPickParser()
    rv = RivalryParser()
    bi = BetsIOParser()

    ## add parsers to service
    AS.add_parser(bc)
    AS.add_parser(tp)
    AS.add_parser(rv)
    # AS.add_parser(bi)

    ## get the latest matches and their odds for every website
    AS.accumulate_matches()

    ## find out if there are any arbitrages across the sites
    AS.find_arbitrages()


if __name__ == "__main__":
    main()
