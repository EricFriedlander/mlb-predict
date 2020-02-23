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

    # test if pitching stats are correct
    compare_pitching_stats(box_score)


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
    '''Function to test whether batting stats are correct'''

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


    home_data = {'Player' : ['Adam Jones', 'Hyun Soo Kim', 'Nolan Reimold', 'Manny Machado', 'Chris Davis', 'Mark Trumbo', 'Matt Wieters', 'Pedro Alvarez',
                                'Jonathan Schoop', 'Ryan Flaherty', 'Joey Rickard', 'Tyler Wilson', 'Dylan Bundy', 'Brian Duensing', 'Vance Worley', 
                                'Team Totals'],
                    'Position' : ['CF', 'LF', 'PH', 'SS', '1B', 'RF', 'C', 'DH', '2B', '3B', 'PH', 'P', 'P', 'P', 'P', 'Total'],
                    'AB' : [4, 4, 1, 4, 4, 4, 3, 4, 4, 2, 1, np.nan, np.nan, np.nan, np.nan, 35],
                    'R' : [1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, np.nan, np.nan, np.nan, np.nan, 6], 
                    'H' : [1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, np.nan, np.nan, np.nan, np.nan, 8],
                    'RBI' : [3, 0, 0, 0, 0, 1, 0, 2, 0, 0, 0, np.nan, np.nan, np.nan, np.nan, 6],
                    'BB' : [1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, np.nan, np.nan, np.nan, np.nan, 3],
                    'SO' : [0, 0, 1, 0, 4, 1, 0, 1, 2, 0, 0, np.nan, np.nan, np.nan, np.nan, 9],
                    'PA' : [5, 4, 1, 4, 4, 4, 4, 4, 4, 3, 1, np.nan, np.nan, np.nan, np.nan, 38],
                    'BA' : [0.242, 0.382, 0.296, 0.311, 0.213, 0.296, 0.281, 0.217, 0.264, 0.2, 0.247, np.nan, np.nan, np.nan, np.nan, 0.229],
                    'OBP' : [0.297, 0.455, 0.341, 0.377, 0.335, 0.348, 0.324, 0.301, 0.291, 0.299, 0.306, np.nan, np.nan, np.nan, np.nan, 0.289],
                    'SLG' : [0.407, 0.5, 0.519, 0.598, 0.431, 0.601, 0.422, 0.408, 0.452, 0.227, 0.354, np.nan, np.nan, np.nan, np.nan, 0.514],
                    'OPS' : [0.704, 0.955, 0.859, 0.975, 0.766, 0.949, 0.746, 0.71, 0.743, 0.526, 0.66, np.nan, np.nan, np.nan, np.nan, 0.804],
                    'Pit' : [17, 13, 5, 16, 17, 14, 22, 18, 14, 12, 4, np.nan, np.nan, np.nan, np.nan, 152],
                    'Str' : [10, 9, 4, 10, 13, 12, 9, 11, 12, 8, 3, np.nan, np.nan, np.nan, np.nan, 101],
                    'WPA' : [0.14, -0.04, -0.049, -0.082, -0.07, -0.083, -0.036, -0.016, -0.011, 0.067, -0.031, np.nan, np.nan, np.nan, np.nan, -0.211],
                    'aLI' : [1.1, 0.91, 1.69, 0.81, 0.65, 0.92, 0.8, 0.71, 1.27, 0.77, 1.23, np.nan, np.nan, np.nan, np.nan, 0.94],
                    'WPA+' : [0.202, 0.04, 0, 0.002, 0, 0.01, 0.028, 0.04, 0.079, 0.077, 0, np.nan, np.nan, np.nan, np.nan, 0.478],
                    'WPA-' : [-0.062, -0.08, -0.049, -0.085, -0.07, -0.093, -0.064, -0.056, -0.09, -0.01, -0.031, np.nan, np.nan, np.nan, np.nan, -0.69],
                    'RE24' : [0.9, -0.2, -0.3, -0.6, -0.8, 0.4, 0.4, 1.2, 0.3, 0.3, -0.2, np.nan, np.nan, np.nan, np.nan, 1.3],
                    'PO' : [5, 0, np.nan, 1, 10, 1, 6, np.nan, 1, 0, np.nan, 0, 1, 1, 1, 27],
                    'A': [0, 0, np.nan, 3, 3, 0, 0, np.nan, 4, 1, np.nan, 2, 0, 0, 0, 13],
                    'Details' : ['HR', '2B', np.nan, np.nan, np.nan, 'HR', np.nan, 'HR', np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
                    }
    home_df = pd.DataFrame(home_data)

    # Ensure the scraped away batting is correct
    pd.testing.assert_frame_equal(box_score.away_batting, away_df)
    pd.testing.assert_frame_equal(box_score.home_batting, home_df)


def compare_pitching_stats(box_score):
    '''Function to test whether pitching stats are correct'''

    # Manually code correct batting dataframes
    away_data = {'Player' : ['Ivan Nova', 'Nick Goody', 'Andrew Miller', 'Aroldis Chapman', 'Team Totals'],
                    'Details' : ['W (4-3)', np.nan, 'H (8)', 'S (9)', 'Total'],
                    'IP' : [6, 0, 2, 1, 9],
                    'H' : [7, 1, 0, 0, 8],
                    'R' : [5, 1, 0, 0, 6],
                    'ER' : [5, 1, 0, 0, 6],
                    'BB' : [2, 0, 0, 1, 3],
                    'SO' : [6, 0, 2, 1, 9],
                    'HR' : [2, 1, 0, 0, 3],
                    'ERA' : [4.41, 4.3, 1.14, 2.38, 6],
                    'BF' : [27, 1, 6, 4, 38],
                    'Pit' : [103, 2, 28, 19, 152],
                    'Str' : [71, 1, 17, 12, 101],
                    'Ctct' : [44, 1, 7, 3, 55],
                    'StS' : [13, 0, 6, 4, 23],
                    'StL' : [14, 0, 4, 5, 23],
                    'GB' : [8, 0, 2, 0, 10],
                    'FB' : [11, 1, 2, 2, 16],
                    'LD' : [5, 0, 0, 0, 5],
                    'Unk' : [0, 0, 0, 0, 0],
                    'GSc' : [42, np.nan, np.nan, np.nan, 42],
                    'IR' : [np.nan, 2, 0, 0, 2],
                    'IS' : [np.nan, 2, 0, 0, 2],
                    'WPA' : [0.066, -0.203, 0.254, 0.095, 0.212],
                    'aLI' : [0.63, 2.06, 1.65, 1.4, 0.94],
                    'RE24' : [-0.9, -2, 1, 0.5, -1.3]
                    }
    away_df = pd.DataFrame(away_data)


    home_data = {'Player' : ['Tyler Wilson', 'Dylan Bundy', 'Brian Duensing', 'Vance Worley', 'Team Totals'],
                    'Details' : ['L (2-5)', np.nan, np.nan, np.nan, 'Total'],
                    'IP' : [4, 2.2, 1.2, 0.2, 9],
                    'H' : [7, 5, 1, 3, 16],
                    'R' : [5, 2, 0, 1, 8],
                    'ER' : [5, 2, 0, 1, 8],
                    'BB' : [0, 0, 0, 0, 0],
                    'SO' : [1, 3, 1, 0, 5],
                    'HR' : [0, 0, 0, 0, 0],
                    'ERA' : [4.39, 4.94, 6.75, 2.62, 8],
                    'BF' : [19, 13, 6, 4, 42],
                    'Pit' : [70, 51, 20, 13, 154],
                    'Str' : [42, 36, 15, 8, 101],
                    'Ctct' : [29, 23, 9, 8, 69],
                    'StS' : [4, 3, 2, 0, 9],
                    'StL' : [9, 10, 4, 0, 23],
                    'GB' : [11, 3, 3, 3, 20],
                    'FB' : [7, 7, 2, 1, 17],
                    'LD' : [3, 4, 2, 1, 10],
                    'Unk' : [0, 0, 0, 0, 0],
                    'GSc' : [29, np.nan, np.nan, np.nan, 29],
                    'IR' : [np.nan, 0, 0, 0, 0],
                    'IS' : [np.nan, 0, 0, 0, 0],
                    'WPA' : [-0.246, -0.026, 0.072, -0.089, -0.289],
                    'aLI' : [0.87, 0.2, 0.47, 0.62, 0.57],
                    'RE24' : [-2.9, -0.6, 0.9, -0.7, -3.3]
                    }
    home_df = pd.DataFrame(home_data)

    # Ensure the scraped away batting is correct
    pd.testing.assert_frame_equal(box_score.away_pitching, away_df)
    pd.testing.assert_frame_equal(box_score.home_pitching, home_df)
