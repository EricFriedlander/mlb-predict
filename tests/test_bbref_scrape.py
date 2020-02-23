'''
test_bbref_scrape.py
Author: Eric Friedlander
This file is design to be called by pytest to test bbref_scrape.py,
the script for scraping data off of baseball reference.
'''

import pandas as pd
import numpy as np
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

    # test if battings stats are correct
    compare_batting_stats(box_score)


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
    pd.testing.assert_frame_equal(df, box_score.linescore)


def compare_batting_stats(box_score):
    '''Function to test whether batting stats is correct'''

    # Manually code correct batting dataframes
    away_data = {'Player' : ['Jacoby Ellsbury', 'Brett Gardner', 'Carlos Beltran', 'Aaron Hicks', 'Alex Rodriguez', 'Starlin Castro', 'Didi Gregorius', 
                                'Chase Headley', 'Rob Refsnyder', 'Chris Parmelee', 'Austin Romine', 'Brian McCann', 'Ivan Nova', 'Nick Goody',
                                'Andrew Miller', 'Aroldis Chapman', 'Team Totals'],
                    'Position' : ['CF', 'LF', 'RF', 'RF', 'DH', '2B', 'SS', '3B', '1B', '1B', 'C', 'C', 'P', 'P', 'P', 'P', 'Total'],
                    'AB' : [5, 5, 4, 1, 5, 5, 5, 4, 4, 0, 3, 0, np.nan, np.nan, np.nan, np.nan, 41],
                    'R' : [1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, np.nan, np.nan, np.nan, np.nan, 8], 
                    'H' : [2, 2, 1, 1, 3, 3, 1, 1, 1, 0, 1, 0, np.nan, np.nan, np.nan, np.nan, 16],
                    'RBI' : [0, 0, 0, 0, 1, 2, 1, 0, 1, 0, 2, 0, np.nan, np.nan, np.nan, np.nan, 7],
                    'BB' : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, np.nan, np.nan, np.nan, np.nan, 0],
                    'SO' : [0, 0, 0, 0, 2, 1, 0, 0, 2, 0, 0, 0, np.nan, np.nan, np.nan, np.nan, 5],
                    'PA' : [5, 5, 4, 1, 5, 5, 5, 4, 4, 0, 4, 0, np.nan, np.nan, np.nan, np.nan, 42],
                    'BA' : [0.28, 0.225, 0.269, 0.202, 0.2, 0.254, 0.263, 0.239, 0.294, np.nan, 0.292, 0.224, np.nan, np.nan, np.nan, np.nan, 0.39],
                    'OBP' : [0.342, 0.351, 0.3, 0.268, 0.257, 0.292, 0.29, 0.317, 0.294, np.nan, 0.309, 0.321, np.nan, np.nan, np.nan, np.nan, 0.381],
                    'SLG' : [0.417, 0.343, 0.528, 0.303, 0.438, 0.415, 0.371, 0.321, 0.529, np.nan, 0.462, 0.401, np.nan, np.nan, np.nan, np.nan, 0.488],
                    'OPS' : [0.759, 0.695, 0.828, 0.571, 0.695, 0.706, 0.661, 0.637, 0.824, np.nan, 0.77, 0.723, np.nan, np.nan, np.nan, np.nan, 0.869],
                    'Pit' : [20, 19, 13, 3, 24, 15, 18, 12, 15, np.nan, 15, np.nan, np.nan, np.nan, np.nan, np.nan, 154],
                    'Str' : [13, 13, 6, 2, 15, 10, 15, 9, 9, np.nan, 9, np.nan, np.nan, np.nan, np.nan, np.nan, 101],
                    'WPA' : [-0.017, -0.045, 0.016, 0.033, 0.118, 0.132, -0.039, 0.024, 0.021, np.nan, 0.046, np.nan, np.nan, np.nan, np.nan, np.nan, 0.289],
                    'aLI' : [0.44, 0.48, 0.43, 0.52, 0.72, 0.66, 0.46, 0.53, 0.81, 0, 0.7, 0, np.nan, np.nan, np.nan, np.nan, 0.57],
                    'WPA+' : [0.024, 0.011, 0.036, 0.033, 0.143, 0.149, 0.009, 0.067, 0.063, np.nan, 0.066, np.nan, np.nan, np.nan, np.nan, np.nan, 0.601],
                    'WPA-' : [-0.042, -0.056, -0.02, 0, -0.025, -0.017, -0.047, -0.043, -0.042, np.nan, -0.019, np.nan, np.nan, np.nan, np.nan, np.nan, -0.311],
                    'RE24' : [0.5, 0, -0.4, 0.4, 1.6, 2.3, -1.4, -0.6, 0.3, 0, 0.7, 0, np.nan, np.nan, np.nan, np.nan, 3.3],
                    'PO' : [1, 4, 1, 0, np.nan, 1, 1, 1, 7, 2, 7, 1, 1, 0, 0, 0, 27],
                    'A': [0, 0, 0, 0, np.nan, 0, 1, 2, 1, 0, 1, 0, 1, 0, 0, 0, 6],
                    'Details' : ['SB', 'SB', np.nan, '2B', np.nan, '2B', 'GDP', '2B', '2B', np.nan, 'SF', np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
                    }
    away_df = pd.DataFrame(away_data)
    # import pdb; pdb.set_trace()
    # Ensure the scraped away batting is correct
    pd.testing.assert_frame_equal(box_score.away_batting, away_df)
