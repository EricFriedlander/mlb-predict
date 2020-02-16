'''
bbref_scrape.py
Author: Eric Friedlander
This file is used for scraping data off of baseball reference.
'''

import requests
import bs4
import pandas as pd

class boxScore(object):
    """Represents a box score from baseball reference.
    
    Attributes:

    Constructor takes:

    """

class boxScoreScraper(object):
    """Scraped a box score off of baseball reference.
    
    Attributes:

    Constructor takes:
    url: address on baseball reference where box score is stored
    """

    def __init__(self, url):
        self.url = url

    def scrape_box_score(self):
        """Scrapes all attributes from url."""
        self.webpage = requests.get(self.url)
        self.soup = bs4.BeautifulSoup(self.webpage)
        self.get_game_overview()

    def get_game_overview(self):
        """Scrapes basic overview of game including runs in each inning, hits, errors, final score, teams, and pitchers."""
        high_level = soup.select("th~ th+ th , td+ .center , .center+ td , tfoot td , .center+ .center")
        [pt.get_text() for pt in high_level]
        
