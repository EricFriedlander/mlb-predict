import pandas as pd
import pandas as pd
import numpy as np
import datetime

def clean_team_season_data(team_level, game_level):
    """Cleaning team and game level data from a single season to prepare for modeling.
    
    Args:
    team_level (DataFrame): a dataframe with team level data after being parsed by bbref_scrape.parse_box_scores. All data shoudl be for one season
    game_level (DataFrame): contains game level data output by bbref_scrape.parse_box_scores


    Returns:
    DataFrame: return DataFrame of cleaned data

    """

    # Select necessary data from team_level dataset
    team_data = team_level[['GameID', 'Team', 'GameNum', 'Opponent', 'GameNumOpponent', 'HomeAway', 'Runs', 'Hits', 'Errors', 'AB', 
                        'RBI', 'BB', 'SO', 'PA', 'OBP', 'SLG', 'Starter']].astype({'GameID' : 'int',
                                                                                                 'Team' : 'category',
                                                                                                 'GameNum' : 'int',
                                                                                                 'Opponent' : 'category',
                                                                                                 'GameNumOpponent' : 'int',
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
    
    # Join opponent statistics
    team_data = team_data.merge(team_data.copy(), how='left', left_on=['GameID', 'Opponent'], right_on=['GameID', 'Team'], suffixes=('', '_Opp'))

    # Compute numerator for OBP and SLG
    # Note that the denominator of OBP is not technically plate appearances. There are some rare events which not counted such as sacrifice bunts but this is a very close approximation
    team_data['OBP_NUM'] = team_data['OBP']*team_data['PA']
    team_data['SLG_NUM'] = team_data['SLG']*team_data['AB']
    team_data['OBP_NUM_Opp'] = team_data['OBP_Opp']*team_data['PA_Opp']
    team_data['SLG_NUM_Opp'] = team_data['SLG_Opp']*team_data['AB_Opp']

    # Compute cumulative means
    mean_vars = ['Runs_Mean', 'Hits_Mean', 'Errors_Mean', 'RBI_Mean', 'BB_Mean', 'SO_Mean', 'Runs_Mean_Opp', 'Hits_Mean_Opp', 
                'Errors_Mean_Opp', 'RBI_Mean_Opp', 'BB_Mean_Opp', 'SO_Mean_Opp']
    to_mean = ['Runs', 'Hits', 'Errors', 'RBI', 'BB', 'SO', 'Runs_Opp', 'Hits_Opp', 'Errors_Opp', 'RBI_Opp', 'BB_Opp', 'SO_Opp']
    team_data.sort_values(by='GameNum', inplace=True)
    team_data[mean_vars] = (team_data.groupby(by='Team').expanding()
                                                       .mean()[to_mean].reset_index(level=0, drop=True))

    # Compute cumulative totals
    sum_vars = ['AB_Total', 'PA_Total', 'OBP_NUM_Total', 'SLG_NUM_Total',
          'AB_Total_Opp', 'PA_Total_Opp', 'OBP_NUM_Total_Opp', 'SLG_NUM_Total_Opp']
    to_sum = ['AB', 'PA', 'OBP_NUM', 'SLG_NUM', 'AB_Opp', 'PA_Opp', 'OBP_NUM_Opp', 'SLG_NUM_Opp']
    team_data[sum_vars] = (team_data.groupby(by='Team').expanding().sum()[to_sum].reset_index(level=0, drop=True))
    
    # Compute cumulative slugging and on-base percentage
    team_data['SLG_Mean'] = team_data['SLG_NUM_Total'] / team_data['PA_Total']
    team_data['OBP_Mean'] = team_data['OBP_NUM_Total'] / team_data['AB_Total']
    team_data['SLG_Mean_Opp'] = team_data['SLG_NUM_Total_Opp'] / team_data['PA_Total_Opp']
    team_data['OBP_Mean_Opp'] = team_data['OBP_NUM_Total_Opp'] / team_data['AB_Total_Opp']

    # Lag data
    potential_features = ['Runs_Mean', 'Hits_Mean', 'Errors_Mean', 'RBI_Mean', 'BB_Mean', 'SO_Mean', 'SLG_Mean', 'OBP_Mean',
                     'Runs_Mean_Opp', 'Hits_Mean_Opp', 'Errors_Mean_Opp', 'RBI_Mean_Opp', 'BB_Mean_Opp', 'SO_Mean_Opp', 
                      'SLG_Mean_Opp', 'OBP_Mean_Opp']
    team_data[potential_features] = team_data.groupby(by='Team')[potential_features].shift(1)

    # Join defensive data from opponent onto team_data
    defensive_stats = ['GameID', 'Team', 'Runs_Mean_Opp', 'Hits_Mean_Opp', 'Errors_Mean_Opp', 'RBI_Mean_Opp', 'BB_Mean_Opp', 
                        'SO_Mean_Opp', 'SLG_Mean_Opp', 'OBP_Mean_Opp']
    team_data =  team_data = team_data.merge(team_data[defensive_stats].copy(), how='left', left_on=['GameID', 'Opponent'], 
                                         right_on=['GameID', 'Team'], suffixes=('', '_Def'))
    return team_data