import pandas as pd
import pandas as pd
import numpy as np
import datetime

def clean_season_data(team_level, game_level, odds):
    """Cleaning team and game level data from a single season to prepare for modeling.
    
    Args:
    team_level (DataFrame): a dataframe with team level data after being parsed by bbref_scrape.parse_box_scores. All data shoudl be for one season
    game_level (DataFrame): contains game level data output by bbref_scrape.parse_box_scores
    odds (DataFrame): contains odds for each game


    Returns:
    DataFrame: return DataFrame of cleaned data

    """

    # Select necessary data from team_level dataset
    team_data = team_level[['GameID', 'Team', 'GameNum', 'HomeAway', 'Runs', 'Hits', 'Errors', 'AB', 
                        'RBI', 'BB', 'SO', 'PA', 'OBP', 'SLG', 'Starter']].astype({'GameID' : 'int',
                                                                                                 'Team' : 'category',
                                                                                                 'GameNum' : 'int',
                                                                                                 'HomeAway' : 'category',
                                                                                                 'Runs' : 'int',
                                                                                                 'Hits' : 'int',
                                                                                                 'Errors' : 'int',
                                                                                                 'AB': 'int',
                                                                                                 'RBI' : 'int', 
                                                                                                 'BB' : 'int', 
                                                                                                 'SO' : 'int', 
                                                                                                 'PA' : 'int', 
                                                                                                 'OBP' : 'float', 
                                                                                                 'SLG' : 'float', 
                                                                                                 'Starter' : 'category'}, copy=False)

    # Compute numerator for OBP and SLG
    # Note that the denominator of OBP is not technically plate appearances. There are some rare events which not counted such as sacrifice bunts but this is a very close approximation
    team_data['OBP_NUM'] = team_data['OBP']*team_data['PA']
    team_data['SLG_NUM'] = team_data['SLG']*team_data['AB']

    # Compute cumulative means
    team_data.sort_values(by='GameNum', inplace=True)
    team_data[['Runs_Mean', 'Hits_Mean', 'Errors_Mean', 'RBI_Mean', 'BB_Mean', 'SO_Mean']] = (team_data.groupby(by='Team')
                                                       .expanding()
                                                       .mean()[['Runs', 'Hits', 'Errors', 'RBI', 'BB', 'SO']].reset_index(level=0, drop=True))

    # Compute cumulative totals
    team_data[['AB_Total', 'PA_Total', 'OBP_NUM_Total', 'SLG_NUM_Total']] = (team_data.groupby(by='Team')
                                                                         .expanding()
                                                                         .sum()[['AB', 'PA', 'OBP_NUM', 'SLG_NUM']].reset_index(level=0, drop=True))

    # Compute cumulative slugging and on-base percentage
    team_data['SLG_Mean'] = team_data['SLG_NUM_Total'] / team_data['PA_Total']
    team_data['OBP_Mean'] = team_data['OBP_NUM_Total'] / team_data['AB_Total']

    # Lag data
    potential_features = ['Runs_Mean', 'Hits_Mean', 'Errors_Mean', 'RBI_Mean', 'BB_Mean', 'SO_Mean', 'SLG_Mean', 'OBP_Mean']
    team_data[potential_features] = team_data.groupby(by='Team')[potential_features].shift(1)

    # Add team abbreviations to dataframe
    team_abbrv = {'Atlanta Braves' : 'ATL', 
              'Arizona Diamondbacks' : 'ARI', 
              'Baltimore Orioles' : 'BAL', 
              'Boston Red Sox' : 'BOS', 
              'Chicago Cubs' : 'CUB', 
              'Chicago White Sox' : 'CWS', 
              'Cincinnati Reds' : 'CIN', 
              'Cleveland Indians' : 'CLE', 
              'Colorado Rockies' : 'COL', 
              'Detroit Tigers' : 'DET',
              'Kansas City Royals': 'KAN', 
              'Houston Astros' : 'HOU', 
              'Los Angeles Angels' : 'LAA', 
              'Los Angeles Dodgers' : 'LAD', 
              'Miami Marlins' : 'MIA', 
              'Florida Marlins' : 'FLA', 
              'Milwaukee Brewers' : 'MIL', 
              'Minnesota Twins' : 'MIN', 
              'New York Mets' : 'NYM', 
              'New York Yankees' : 'NYY', 
              'Oakland Athletics' : 'OAK',
              'Philadelphia Phillies' : 'PHI', 
              'Pittsburgh Pirates' : 'PIT', 
              'San Diego Padres' : 'SDG', 
              'Seattle Mariners' : 'SEA', 
              'San Francisco Giants' : 'SFO', 
              'St. Louis Cardinals' : 'STL', 
              'Tampa Bay Rays' : 'TAM', 
              'Texas Rangers' : 'TEX', 
              'Toronto Blue Jays' : 'TOR', 
              'Washington Nationals' : 'WAS'}
    team_data['TeamAbr'] = team_data['Team'].apply(lambda x: team_abbrv[x])

    # Put dates in simpler format and add too dataframe
    game_date = game_level[['GameID', 'DateTime']].astype({'GameID' : 'int'})
    game_date['Date'] = game_date['DateTime'].map(lambda x: x.month*100 + x.day)
    game_date.drop(columns='DateTime', inplace=True)
    team_data = team_data.merge(game_date, on='GameID')

    # Clean up odds dataframe
    odds.rename(columns={'Team' : 'TeamAbr', 'Final' : 'Runs', 'Unnamed: 18' : 'Line Odds'}, inplace=True)
    team_data = team_data.merge(odds[['Date', 'TeamAbr', 'Runs', 'Run Line', 'Line Odds', 'Pitcher']], how='left', on=['TeamAbr', 'Date', 'Runs'])

    # Add game_level data
    model_data = game_level[['GameID', 'AwayTeam', 'HomeTeam', 'DateTime', 'AwayScore', 'HomeScore']].astype({
    'AwayScore' : 'int',
    'HomeScore' : 'int'
    })
    model_data = model_data.merge(team_data, left_on=['GameID', 'AwayTeam'], right_on=['GameID', 'Team'])
    model_data = model_data.merge(team_data, left_on=['GameID', 'HomeTeam'], right_on=['GameID', 'Team'], suffixes=('_away', '_home'))
    model_data['ScoreDiff'] = model_data['AwayScore'] - model_data['HomeScore']
    model_data.drop(columns=['Team_away', 'Team_home', 'Runs_away', 'Runs_home'], inplace=True)

    return model_data