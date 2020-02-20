'''
bbref_scrape.py
Author: Eric Friedlander
This file is used for scraping data off of baseball reference.
'''

import requests
import bs4
import pandas as pd
import re
class BoxScore(object):
    """Represents a box score from baseball reference.
    
    Attributes:
    linescore: dataframe with runs for each team over all innings and hits, error, and final score

    Constructor takes:

    """

    def set_linescore(self, df):
        self.linescore = df

class BoxScoreScraper(object):
    """Scraped a box score off of baseball reference.
    
    Attributes:

    Constructor takes:
    url: address on baseball reference where box score is stored
    """

    def __init__(self, url):
        self.url = url

    def scrape_box_score(self):
        """Scrapes all attributes from url."""
        self.response = requests.get(self.url)

        # Comments cause scraping to fail so we must remove them then and scrape
        comments = re.compile("<!--|-->")
        self.soup = bs4.BeautifulSoup(comments.sub('', self.response.text), 'lxml')
        self.divs = self.soup.find('div', id = "content")

        # Create boxScore object to be populated
        self.box_score = BoxScore()

        # Scrape linescore table
        self.scrape_linescore()

    def scrape_linescore(self):
        """Scrapes basic overview of game including runs in each inning, hits, errors, final score, teams, and pitchers."""
        table = self.divs.find('table', {'class' : "linescore"})
        df = pd.read_html(table.prettify(), flavor='lxml')[0]
        df = df.drop(df.columns[0], axis=1)
        df = df.drop(2)
        df.rename(columns = {df.columns[0] : 'Team'}, inplace=True)
        df[df.columns[1:]] = df[df.columns[1:]].astype('int')
        self.box_score.set_linescore(df)