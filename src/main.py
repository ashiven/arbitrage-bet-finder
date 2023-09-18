from arbitrage.bettype import BetType
from arbitrage.parsers import (
    BCGameParser,
    BetsIOParser,
    RivalryParser,
    ThunderPickParser,
    TrustDiceWinParser,
)
from arbitrage.service import ArbitrageService


def main():
    # (the SOCCER variant does not work yet)
    AS = ArbitrageService(variant=BetType.CS, verbose=False, retries=5)

    ## initialize parsers
    bc = BCGameParser()
    tp = ThunderPickParser()
    rv = RivalryParser()
    bi = BetsIOParser()
    tw = TrustDiceWinParser()

    ## add parsers to service
    # AS.add_parser(bc)
    # AS.add_parser(tp)
    # AS.add_parser(rv)
    # AS.add_parser(bi)
    AS.add_parser(tw)

    ## get the latest matches and their odds for every website
    AS.accumulate_matches()

    ## find out if there are any arbitrages across the sites
    AS.find_arbitrages()


if __name__ == "__main__":
    main()
