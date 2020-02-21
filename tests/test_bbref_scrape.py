'''
test_bbref_scrape.py
Author: Eric Friedlander
This file is design to be called by pytest to test bbref_scrape.py,
the script for scraping data off of baseball reference.
'''

import sys
import pandas as pd
import pdb
sys.path.append('/Users/efriedlander/Dropbox/SportsBetting/mlb-predict')
from src.data import bbref_scrape

def test_BoxScoreScraper():
    '''Function for testing the main box score scraper. This is done by comparing to
    the Yankees-Orioles game played on July4th, 2016.'''

    # hardcode correct url for game
    url = 'https://www.baseball-reference.com/boxes/BAL/BAL201606040.shtml'

    # create scraper object and scrape box score
    scraper = bbref_scrape.BoxScoreScraper(url)
    scraper.scrape_box_score()

    # retrieve box score object from scraper
    box_score = scraper.box_score

    # test if scorebox info is correct
    compare_scorebox(box_score)

    # test if linescore is correct
    compare_linescore(box_score)


def compare_scorebox(box_score):
    '''Function to test whether scorebox info is correct'''
    assert(box_score.away_team == 'New York Yankees')
    assert(box_score.home_team == 'Baltimore Orioles')
    assert(box_score.date == 'Saturday, June 4, 2016')
    assert(box_score.time == '7:18 p.m. Local')
    assert(box_score.attendance == 33170)
    assert(box_score.venue == 'Oriole Park at Camden Yards')
    assert(box_score.duration == '3:25')
    assert(box_score.time_place == 'Night Game, on grass')


def compare_linescore(box_score):
    '''Function to test whether linescore is correct'''

    # Manually code correct linescore dataframe
    data = {'Team' : ['New York Yankees', 'Baltimore Orioles'],
                    '1' : [0, 0],
                    '2' : [0, 0],
                    '3' : [1, 0],
                    '4' : [4, 0],
                    '5' : [1, 0],
                    '6' : [1, 0],
                    '7' : [0, 6],
                    '8' : [0, 0],
                    '9' : [1, 0],
                    'R' : [8, 6],
                    'H' : [16, 8],
                    'E' : [0, 0]}
    df = pd.DataFrame(data)

    # Ensure the scraped linescore is correct
    assert(df.equals(box_score.linescore))
