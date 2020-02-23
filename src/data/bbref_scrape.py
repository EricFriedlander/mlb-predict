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

    def set_score_box_info(self, away, home, date, time, attendance, venue, duration, time_place):
        """Sets all values associated with the score_box"""
        self.away_team = away
        self.home_team = home
        self.date = date
        self.time = time
        self.attendance = attendance
        self.venue = venue
        self.duration = duration
        self.time_place = time_place

       
    def set_linescore(self, df):
        """ Sets the linescore"""
        self.linescore = df

    def set_away_batting(self, df):
        """ Sets batting stats for away team"""
        self.away_batting = df

    def set_home_batting(self, df):
        """ Sets batting stats for home team"""
        self.home_batting = df

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
        self.content = self.soup.find('div', id = "content")

        # Create boxScore object to be populated
        self.box_score = BoxScore()

        # Scrape scorebox
        self.scrape_scorebox()

        # Scrape linescore table
        self.scrape_linescore()

        # Scrape batting data
        self.box_score.set_away_batting(self.scrape_batting(self.box_score.away_team))
        self.box_score.set_home_batting(self.scrape_batting(self.box_score.home_team))

    def scrape_scorebox(self):
        """Scrapes data from scorebox including home/away teams, date, start time, attendance, venue, duration, 
        then puts it in the classes BoxScore object."""
        scorebox = self.content.find('div', {'class' : 'scorebox'})

        # Get home/away teams
        teams = scorebox.find_all('a', {'itemprop' : "name"})
        away_team = teams[0].text
        home_team = teams[1].text

        # Get meta information
        scorebox_meta = scorebox.find('div', {'class' : 'scorebox_meta'}).find_all('div')
        date = scorebox_meta[0].text
        time = scorebox_meta[1].text.split(':', 1)[1].strip()
        attendance = scorebox_meta[2].text.split(':', 1)[1].strip()
        attendance = int(attendance.replace(',', ''))
        venue = scorebox_meta[3].text.split(':', 1)[1].strip()
        duration = scorebox_meta[4].text.split(':', 1)[1].strip()
        time_place = scorebox_meta[5].text.strip()

        # Put information in BoxScore object
        self.box_score.set_score_box_info(away_team, home_team, date, time, attendance, venue, duration, time_place)

    def scrape_linescore(self):
        """Scrapes basic overview of game including runs in each inning, hits, errors, final score, teams, and pitchers, 
        then puts it in the classes BoxScore object."""
        table = self.content.find('table', {'class' : "linescore"})
        df = pd.read_html(table.prettify(), flavor='lxml')[0]
        df = df.drop(df.columns[0], axis=1)
        df = df.drop(2)
        df.rename(columns = {df.columns[0] : 'Team'}, inplace=True)
        df[df.columns[1:]] = df[df.columns[1:]].astype('int')
        self.box_score.set_linescore(df)

    def scrape_batting(self, team):
        """Scrapes data from the batting table corresponding to the team (string) given as input returns dataframe of batting stats.
            Returns Dataframe of batting stats."""
        
        # Get data, read to dataframe, clean/renaming some columns for readability
        batting = self.content.find('table', id=team.replace(' ', '') + 'batting')
        df = pd.read_html(batting.prettify(), flavor='lxml')[0]
        df.rename(columns = {'Batting' : 'Player'}, inplace=True)
        df.dropna(subset=['Player'], inplace=True)
        df.reset_index(inplace=True)

        # Split out player name from positions and assign to new columns making sure to deal with team totals correctly
        player_split = df['Player'][:-1].str.rsplit(' ', n=1, expand=True)
        df['Player'][:-1] = player_split[0].str.strip()
        player_split[1][len(player_split[1])] = 'Total'
        df.insert(1, 'Position', player_split[1])

        return df