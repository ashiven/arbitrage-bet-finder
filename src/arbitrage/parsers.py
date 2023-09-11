import re
import requests
from time import sleep
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from arbitrage.bettype import BetType


class MatchParser(ABC):
    ## not all sites require a login to view match information
    @abstractmethod
    def login(self):
        pass

    @abstractmethod
    def get_matches(self):
        pass


## helper functions
def create_driver(headless=True):
    service = Service("C:\Program Files (x86)\Google\chromedriver.exe")
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("headless")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    caps = DesiredCapabilities.CHROME
    caps["pageLoadStrategy"] = "normal"
    driver = webdriver.Chrome(
        service=service, options=options, desired_capabilities=caps
    )
    return driver


def await_elem(driver, delay, by, id):
    try:
        return WebDriverWait(driver, delay).until(
            EC.presence_of_element_located((by, id))
        )
    except:
        print("Loading element took too long.")


class BCGameParser(MatchParser):
    def __init__(self):
        self.website = "bc.game"
        self.matches = dict()
        self.session = requests.session()

    def configure(self, retries, variant, verbose):
        URLS = {
            BetType.CS: "https://bc.game/sports?bt-path=%2F%3FtopSport%3Dcounter-strike-109",
            BetType.SOCCER: "https://bc.game/sports?bt-path=%2Fsoccer-1",
        }
        self.retries = retries
        self.url = URLS[variant]
        self.verbose = verbose

    def login(self, username, password):
        try:
            r = self.session.get("https://bc.game/#/login", auth=(username, password))
            assert r.status_code == 200
        except:
            print("something went wrong logging in")

    def get_matches(self):
        print(f"[+] Getting matches from {self.website}")
        driver = create_driver()

        for _ in range(self.retries):
            try:
                driver.get(self.url)
                shadow_host = await_elem(driver, 3, By.CSS_SELECTOR, "#bt-inner-page")

                shadow_root = driver.execute_script(
                    "return arguments[0].shadowRoot;", shadow_host
                )
                container = shadow_root.find_element(
                    By.CSS_SELECTOR,
                    "[style*='overflow: visible;']",
                )
                soup = BeautifulSoup(
                    container.get_attribute("outerHTML"), "html.parser"
                )
                bet_container = soup.find_all("span")
                bets = [
                    span
                    for span in bet_container
                    if span.get_text(strip=True, separator=" ").strip() != ""
                ]

                team_pattern = r"[a-zA-Z]"
                for i in range(1, len(bets)):
                    if (
                        i < len(bets) - 1
                        and len(bets[i].text) < 20
                        and len(bets[i + 1].text) < 20
                        and not "over" in bets[i].text
                        and not "under" in bets[i].text
                        and not "over" in bets[i + 1].text
                        and not "under" in bets[i + 1].text
                        and bool(re.match(team_pattern, bets[i].text))
                        and bool(re.match(team_pattern, bets[i + 1].text))
                    ):
                        odds_offset, odd_pattern = i, r"^[-+]?\d*\.\d+$"
                        while not bool(re.match(odd_pattern, bets[odds_offset].text)):
                            odds_offset += 1

                        self.matches[
                            (bets[i].text.upper(), bets[i + 1].text.upper())
                        ] = (
                            float(bets[odds_offset].text),
                            float(bets[odds_offset + 2].text),
                        )

                break

            except Exception as e:
                print(f"[!] Something went wrong getting matches. Retrying...")
                if self.verbose:
                    print(e)


class ThunderPickParser(MatchParser):
    def __init__(self):
        self.website = "thunderpick.io"
        self.matches = dict()
        self.session = requests.session()

    def configure(self, retries, variant, verbose):
        URLS = {
            BetType.CS: "https://thunderpick.io/en/esports/csgo",
            BetType.SOCCER: "https://thunderpick.io/en/sports/football",
        }
        self.retries = retries
        self.url = URLS[variant]
        self.verbose = verbose

    def login(self, username, password):
        pass

    def get_matches(self):
        print(f"[+] Getting matches from {self.website}")
        driver = create_driver()

        for _ in range(self.retries):
            try:
                driver.get(self.url)
                root_container = await_elem(
                    driver, 3, By.CSS_SELECTOR, "#match-list-header"
                )

                soup = BeautifulSoup(
                    root_container.get_attribute("outerHTML"), "html.parser"
                )

                matches = soup.find_all(
                    "div",
                    class_="match-row__container match-row__container--medium match-row__container--no-draw",
                )

                for match in matches:
                    team_one = match.find(
                        "div",
                        class_="match-row__home-name match-row__participant-name",
                    ).text.upper()
                    team_two = match.find(
                        "div",
                        class_="match-row__away-name match-row__participant-name",
                    ).text.upper()

                    odds = match.find_all("span", class_="odds-button__odds")
                    odd_one = float(odds[0].text) if len(odds) > 1 else -1
                    odd_two = float(odds[1].text) if len(odds) > 1 else -1
                    self.matches[(team_one, team_two)] = (odd_one, odd_two)

                break

            except Exception as e:
                print(f"[!] Something went wrong getting matches. Retrying..")
                if self.verbose:
                    print(e)


class RivalryParser(MatchParser):
    def __init__(self):
        self.website = "rivalry.com"
        self.matches = dict()
        self.session = requests.session()

    def configure(self, retries, variant, verbose):
        URLS = {
            BetType.CS: "https://www.rivalry.com/esports/csgo-betting",
            BetType.SOCCER: "https://www.rivalry.com/sports/football-betting",
        }
        self.retries = retries
        self.url = URLS[variant]
        self.verbose = verbose

    def login(self, username, password):
        pass

    def get_matches(self):
        print(f"[+] Getting matches from {self.website}")
        # TODO: find out why this doesn't work in headless mode
        driver = create_driver(headless=False)

        for _ in range(self.retries):
            try:
                driver.get(self.url)

                root_container = await_elem(
                    driver, 3, By.CLASS_NAME, "bet-center-content-markets"
                )
                driver.execute_script(
                    "arguments[0].scrollIntoView(true);", root_container
                )

                soup = BeautifulSoup(
                    root_container.get_attribute("outerHTML"), "html.parser"
                )

                matches = soup.find_all(
                    "div",
                    class_="betline-competitors betline-matchup",
                )

                for match in matches:
                    team_one = match.find(
                        "button",
                        class_="competitor right-facing-competitor right-facing-competitor-desktop",
                    )
                    team_two = match.find(
                        "button",
                        class_="competitor left-facing-competitor left-facing-competitor-desktop",
                    )
                    if not team_one or not team_two:
                        continue

                    team_one_name = team_one.find(
                        "div", class_="outcome-name"
                    ).text.upper()
                    team_one_odds = team_one.find("div", class_="outcome-odds").text
                    team_two_name = team_two.find(
                        "div", class_="outcome-name"
                    ).text.upper()
                    team_two_odds = team_two.find("div", class_="outcome-odds").text

                    self.matches[(team_one_name, team_two_name)] = (
                        float(team_one_odds),
                        float(team_two_odds),
                    )

                break

            except Exception as e:
                print(f"[!] Something went wrong getting matches. Retrying..")
                if self.verbose:
                    print(e)


# TODO:
# - create parser
class ggBetParser(MatchParser):
    def __init__(self):
        self.website = "gg.bet"
        self.matches = dict()
        self.session = requests.session()

    def configure(self, retries, variant, verbose):
        URLS = {
            BetType.CS: "https://gg.bet/en/?sportIds%5B%5D=esports_counter_strike",
            BetType.SOCCER: "https://gg.bet/en/?sportIds%5B%5D=football",
        }
        self.retries = retries
        self.url = URLS[variant]
        self.verbose = verbose

    def login(self, username, password):
        pass

    def get_matches(self):
        print(f"[+] Getting matches from {self.website}")
        driver = create_driver()

        for _ in range(self.retries):
            try:
                driver.get(self.url)
                root_container = await_elem(
                    driver, 3, By.CLASS_NAME, "bet-center-content-markets"
                )

                soup = BeautifulSoup(
                    root_container.get_attribute("outerHTML"), "html.parser"
                )

                matches = soup.find_all(
                    "div",
                    class_="betline-competitors betline-matchup",
                )

                for match in matches:
                    team_one = match.find(
                        "button",
                        class_="competitor right-facing-competitor right-facing-competitor-desktop",
                    )
                    team_two = match.find(
                        "button",
                        class_="competitor left-facing-competitor left-facing-competitor-desktop",
                    )

                    team_one_name = team_one.find(
                        "div", class_="outcome-name"
                    ).text.upper()
                    team_one_odds = team_one.find("div", class_="outcome-odds").text
                    team_two_name = team_two.find(
                        "div", class_="outcome-name"
                    ).text.upper()
                    team_two_odds = team_two.find("div", class_="outcome-odds").text

                    self.matches[(team_one_name, team_two_name)] = (
                        float(team_one_odds),
                        float(team_two_odds),
                    )

                break

            except Exception as e:
                print(f"[!] Something went wrong getting matches. Retrying..")
                if self.verbose:
                    print(e)


class BetsIOParser(MatchParser):
    def __init__(self):
        self.website = "bets.io"
        self.matches = dict()
        self.session = requests.session()

    def configure(self, retries, variant, verbose):
        URLS = {
            BetType.CS: "https://sport.bets.io/en/cs",
            BetType.SOCCER: "https://sport.bets.io/en/soccer",
        }
        self.retries = retries
        self.url = URLS[variant]
        self.verbose = verbose

    def login(self, username, password):
        pass

    def get_matches(self):
        print(f"[+] Getting matches from {self.website}")
        driver = create_driver()

        for _ in range(self.retries):
            try:
                driver.get(self.url)
                sleep(3)

                root_container = await_elem(driver, 3, By.CLASS_NAME, "sb-PageContent")

                soup = BeautifulSoup(
                    root_container.get_attribute("outerHTML"), "html.parser"
                )

                matches = soup.find_all(
                    "div",
                    class_="sb-BettingTable-row",
                )

                for match in matches:
                    teams = match.find_all("span", class_="sb-TeamColumn-name")
                    if not teams:
                        continue
                    team_one_name = teams[0].text.upper()
                    team_two_name = teams[1].text.upper()

                    odds = match.find_all(
                        "div", class_="sb-AnimatedOdd sb-OddsCell-value"
                    )
                    team_one_odds = float(odds[0].text) if len(odds) > 1 else -1
                    team_two_odds = float(odds[1].text) if len(odds) > 1 else -1

                    self.matches[(team_one_name, team_two_name)] = (
                        team_one_odds,
                        team_two_odds,
                    )

                break

            except Exception as e:
                print(f"[!] Something went wrong getting matches. Retrying..")
                if self.verbose:
                    print(e)
