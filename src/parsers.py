import requests
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class MatchParser(ABC):
    ## not all sites require a login to view match information
    @abstractmethod
    def login(self):
        pass

    @abstractmethod
    def get_matches(self):
        pass


class ggBetParser(MatchParser):
    def __init__(self):
        self.matches = dict()
        self.session = requests.session()

    def login(self, username, password):
        try:
            r = self.session.get("https://bc.game/#/login", auth=(username, password))
            assert r.status_code == 200
        except:
            print("something went wrong logging in")

    def get_matches(self):
        service = Service("C:\Program Files (x86)\Google\chromedriver.exe")
        options = webdriver.ChromeOptions()
        caps = DesiredCapabilities.CHROME
        caps["pageLoadStrategy"] = "normal"
        driver = webdriver.Chrome(
            service=service, options=options, desired_capabilities=caps
        )
        RETRIES = 3
        for _ in range(RETRIES):
            try:
                driver.get(
                    "https://bc.game/sports?bt-path=%2F%3FtopSport%3Dcounter-strike-109"
                )
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

                STEP_SIZE = 107
                for i in range(1, len(bets), STEP_SIZE):
                    self.matches[(bets[i].text, bets[i + 1].text)] = (
                        float(bets[i + 3].text),
                        float(bets[i + 5].text),
                    )

                break

            except Exception as e:
                print(f"Something went wrong getting matches. Retrying...")
                print(e)


class ThunderPickParser(MatchParser):
    def __init__(self):
        self.matches = dict()
        self.session = requests.session()

    def login(self, username, password):
        # try:
        #    r = self.driver.get("https://bc.game/#/login", auth=(username, password))
        #    assert r.status_code == 200
        # except:
        #    print("something went wrong logging in")
        pass

    def get_matches(self):
        service = Service("C:\Program Files (x86)\Google\chromedriver.exe")
        options = webdriver.ChromeOptions()
        caps = DesiredCapabilities.CHROME
        caps["pageLoadStrategy"] = "normal"
        driver = webdriver.Chrome(
            service=service, options=options, desired_capabilities=caps
        )
        RETRIES = 3
        for _ in range(RETRIES):
            try:
                driver.get("https://thunderpick.io/en/esports/csgo")
                root_container = driver.find_element(
                    By.CSS_SELECTOR, "#match-list-header"
                )
                soup = BeautifulSoup(
                    root_container.get_attribute("outerHTML"), "html.parser"
                )

                home_teams = soup.find_all(
                    "div", class_="match-row__home-name match-row__participant-name"
                )
                away_teams = soup.find_all(
                    "div", class_="match-row__away-name match-row__participant-name"
                )

                odds = soup.find_all("span", class_="odds-button__odds")

                for i in range(0, len(odds), 2):
                    self.matches[(home_teams[i // 2].text, away_teams[i // 2].text)] = (
                        float(odds[i].text),
                        float(odds[i + 1].text),
                    )

                break

            except Exception as e:
                print(f"Something went wrong getting matches. Retrying..")
                # print(e)
