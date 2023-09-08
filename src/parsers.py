import re
import requests
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bettype import BetType


class MatchParser(ABC):
    ## not all sites require a login to view match information
    @abstractmethod
    def login(self):
        pass

    @abstractmethod
    def get_matches(self):
        pass


class BCGameParser(MatchParser):
    def __init__(self, retries=3, variant=BetType.CSGO, verbose=False):
        URLS = {
            BetType.CSGO: "https://bc.game/sports?bt-path=%2F%3FtopSport%3Dcounter-strike-109",
            BetType.SOCCER: "https://bc.game/sports?bt-path=%2Fsoccer-1",
        }

        self.url = URLS[variant]
        self.website = "bc.game"
        self.verbose = verbose
        self.retries = retries
        self.matches = dict()
        self.session = requests.session()

    def login(self, username, password):
        try:
            r = self.session.get("https://bc.game/#/login", auth=(username, password))
            assert r.status_code == 200
        except:
            print("something went wrong logging in")

    def get_matches(self):
        print("[+] Getting matches from bc.game")
        service = Service("C:\Program Files (x86)\Google\chromedriver.exe")
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        caps = DesiredCapabilities.CHROME
        caps["pageLoadStrategy"] = "normal"
        driver = webdriver.Chrome(
            service=service, options=options, desired_capabilities=caps
        )

        for _ in range(self.retries):
            try:
                driver.get(self.url)
                shadow_host = driver.find_element(By.CSS_SELECTOR, "#bt-inner-page")
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
    def __init__(self, retries=3, variant=BetType.CSGO, verbose=False):
        URLS = {
            BetType.CSGO: "https://thunderpick.io/en/esports/csgo",
            BetType.SOCCER: "https://thunderpick.io/en/sports/football",
        }

        self.website = "thunderpick.io"
        self.verbose = verbose
        self.retries = retries
        self.url = URLS[variant]
        self.matches = dict()
        self.session = requests.session()

    def login(self, username, password):
        pass

    def get_matches(self):
        print("[+] Getting matches from thunderpick.io")
        service = Service("C:\Program Files (x86)\Google\chromedriver.exe")
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        caps = DesiredCapabilities.CHROME
        caps["pageLoadStrategy"] = "normal"
        driver = webdriver.Chrome(
            service=service, options=options, desired_capabilities=caps
        )
        for _ in range(self.retries):
            try:
                driver.get(self.url)
                root_container = driver.find_element(
                    By.CSS_SELECTOR, "#match-list-header"
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
                    odd_one = float(odds[0].text) if len(odds) > 1 else "TBA"
                    odd_two = float(odds[1].text) if len(odds) > 1 else "TBA"
                    self.matches[(team_one, team_two)] = (odd_one, odd_two)

                break

            except Exception as e:
                print(f"[!] Something went wrong getting matches. Retrying..")
                if self.verbose:
                    print(e)
