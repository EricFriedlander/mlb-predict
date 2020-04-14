'''
bbref_scrape.py
Author: Eric Friedlander
This file is used for scraping data off of baseball reference.
'''

import requests
import bs4
import pandas as pd
import re
import numpy as np
import datetime
import dateparser
import time
class BoxScore(object):
    """Represents a box score from baseball reference.
    
    Attributes:
    linescore: dataframe with runs for each team over all innings and hits, error, and final score

    Constructor takes:

    """

    def set_score_box_info(self, away, home, date, time, attendance, venue, duration, time_place, 
                            away_wins, away_losses, home_wins, home_losses):
        """Sets all values associated with the score_box"""
        self.away_team = away
        self.home_team = home
        self.date = date
        self.time = time
        self.attendance = attendance
        self.venue = venue
        self.duration = duration
        self.time_place = time_place
        self.away_wins = away_wins
        self.away_losses = away_losses
        self.away_games = away_wins + away_losses
        self.home_wins = home_wins
        self.home_losses = home_losses
        self.home_games = home_wins+home_losses

       
    def set_linescore(self, df):
        """ Sets the linescore"""
        self.linescore = df

    def set_away_batting(self, df):
        """ Sets batting stats for away team"""
        self.away_batting = df

    def set_home_batting(self, df):
        """ Sets batting stats for home team"""
        self.home_batting = df

    def set_away_pitching(self, df):
        """ Sets pitching stats for away team"""
        self.away_pitching = df

    def set_home_pitching(self, df):
        """ Sets batting stats for home team"""
        self.home_pitching = df


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

        # Scrape pitching data
        self.box_score.set_away_pitching(self.scrape_pitching(self.box_score.away_team))
        self.box_score.set_home_pitching(self.scrape_pitching(self.box_score.home_team))

    def scrape_scorebox(self):
        """Scrapes data from scorebox including home/away teams, date, start time, attendance, venue, duration, 
        then puts it in the classes BoxScore object."""
        scorebox = self.content.find('div', {'class' : 'scorebox'})

        # Get home/away teams and records
        teams = scorebox.find_all('a', {'itemprop' : "name"})
        away_team = teams[0].text
        home_team = teams[1].text
        scorebox_divs = scorebox.find_all('div')
        away_record = scorebox_divs[5].text.split('-')
        home_record = scorebox_divs[5].text.split('-')

        # Get meta information
        scorebox_meta = scorebox.find('div', {'class' : 'scorebox_meta'}).find_all('div')
        date = scorebox_meta[0].text

        # Set everything to NaN in case not included
        time = attendance = venue = duration = time_place = np.nan
        for line in scorebox_meta:
            if 'Start Time' in line.text:
                time = line.text.split(':', 1)[1].strip()
            elif 'Attendance' in line.text:
                attendance = line.text.split(':', 1)[1].strip()
                attendance = int(attendance.replace(',', ''))
            elif 'Venue' in line.text:
                venue = line.text.split(':', 1)[1].strip()
            elif 'Duration' in line.text:
                duration = line.text.split(':', 1)[1].strip()
            elif 'Game, on' in line.text:    
                time_place = line.text.strip()

        # Put information in BoxScore object
        self.box_score.set_score_box_info(away_team, home_team, date, time, attendance, venue, duration, time_place, 
                                            away_record[0], away_record[1], home_record[0], home_record[1])

    def scrape_linescore(self):
        """Scrapes basic overview of game including runs in each inning, hits, errors, final score, teams, and pitchers, 
        then puts it in the classes BoxScore object."""
        table = self.content.find('table', {'class' : "linescore"})
        df = pd.read_html(table.prettify(), flavor='lxml')[0]
        df = df.drop(df.columns[0], axis=1)
        df = df.truncate(after=1, axis='rows')
        df.rename(columns = {df.columns[0] : 'Team'}, inplace=True)
        df[df.columns[1:]] = df[df.columns[1:]].replace('X', None).astype('int')
        self.box_score.set_linescore(df)

    def scrape_batting(self, team):
        """Scrapes data from the batting table corresponding to the team (string) given as input.
            Returns Dataframe of batting stats."""
        
        # Get data, read to dataframe, clean/renaming some columns for readability
        batting = self.content.find('table', id=team.replace(' ', '').replace('.', '') + 'batting')
        df = pd.read_html(batting.prettify(), flavor='lxml')[0]
        df.rename(columns={'Batting' : 'Player'}, inplace=True)
        df.dropna(subset=['Player'], inplace=True)
        df.reset_index(inplace=True, drop=True)

        # Split out player name from positions and assign to new columns making sure to deal with team totals correctly
        player_split = df['Player'][:-1].str.rsplit(' ', n=1, expand=True)
        df.iloc[:-1, df.columns.get_loc('Player')] = player_split[0].str.strip()
        player_split[1][len(player_split[1])] = 'Total'
        df.insert(1, 'Position', player_split[1])

        return df

    def scrape_pitching(self, team):
        """Scrapes data from the pitching table corresponding to the team (string) given as input.
            Returns Dataframe of pitching stats."""
        
        # Get data, read to dataframe, clean/renaming some columns for readability
        pitching = self.content.find('table', id=team.replace(' ', '').replace('.', '') + 'pitching')
        df = pd.read_html(pitching.prettify(), flavor='lxml')[0]
        df.rename(columns= {'Pitching' : 'Player'}, inplace=True)

        # Split out player name from details and assign to new columns making sure to deal with team totals correctly
        player_split = df['Player'][:-1].str.rsplit(', ', n=1, expand=True)
        df.iloc[:-1, df.columns.get_loc('Player')] = player_split[0].str.strip()
        player_split[1][len(player_split[1])] = 'Total'
        df.insert(1, 'Details', player_split[1])

        return df


def get_box_score_links(team, first_date, last_date):
    """ 
    Scrapes links to box score data from a specified team between two dates.
  
    This function navigates to the appropraite team back on baseballreference and then iterates through
    all gaames between the specified dates and scrapes the box score links.
  
    Parameters: 
    Team (str): Team whose data to scrape, must be in the three-character abbreviation:
    'ATL', 'ARI', 'BAL', 'BOS', 'CHC', 'CHW', 'CIN', 'CLE', 'COL', 'DET',
    'KCR', 'HOU', 'LAA', 'LAD', 'MIA', 'FLA', 'MIL', 'MIN', 'NYM', 'NYY', 'OAK',
    'PHI', 'PIT', 'SDP', 'SEA', 'SFG', 'STL', 'TBR', 'TEX', 'TOR', 'WSN',
    'ALL' - denotes all teams
  
    Returns: 
    Dataframe with dates and links to boxscores for all the requested games.

    """

    team_abbrv = ['ATL', 'ARI', 'BAL', 'BOS', 'CHC', 'CHW', 'CIN', 'CLE', 'COL', 'DET',
                    'KCR', 'HOU', 'LAA', 'LAD', 'MIA', 'FLA', 'MIL', 'MIN', 'NYM', 'NYY', 'OAK',
                    'PHI', 'PIT', 'SDP', 'SEA', 'SFG', 'STL', 'TBR', 'TEX', 'TOR', 'WSN']

    if team not in team_abbrv and team != 'ALL':
        raise Exception('Team specified must be one of the three-character abbreviations using in baseball \
                            reference. See docstring for more information.')

    if team == 'ALL':
        team_list = team_abbrv
    else:
        team_list = [team]
    
    # Extract first and last years
    first_year = first_date.year
    last_year = last_date.year

    # Initialize output
    links = pd.DataFrame(columns=['Date', 'URL'])

    # Iterate through each year in range
    for year in range(first_year, last_year+1):
        # Replace MIA with FLA since Florida Marlins became MIAMI Marlins in 2011
        if year <= 2011:
            team_list = ['FLA' if  x=='MIA' else x for x in team_list]
        else:
            team_list = ['MIA' if  x=='FLA' else x for x in team_list]
        # Iterate through each requested team
        for team_iter in team_list:
            # import pdb; pdb.set_trace()
            # Scrape list of games
            url = 'https://www.baseball-reference.com/teams/' + str(team_iter) + '/' + str(year) + '-schedule-scores.shtml'
            res = requests.get(url)
            comm = re.compile("<!--|-->")
            soup = bs4.BeautifulSoup(comm.sub("", res.text), 'lxml')
            content = soup.find('div', id = "content")
            schedule = content.find('table', id='team_schedule')
            print(team_iter, end='\r')
            schedule_rows = schedule.find_all('tr')
            
            # Iterate through rows
            for row in schedule_rows:
                date_col = row.find('td', {'data-stat' : 'date_game'})
                if date_col:
                    # print(date_col.text)
                    date = dateparser.parse(date_col.text.split(' (')[0])
                    date = date.replace(year = year)
                    print(str(date) + '      ', end='\r')
                    # import pdb; pdb.set_trace()
                    if first_date <= date <= last_date:
                        box_url = 'https://www.baseball-reference.com' + row.find('td', {'data-stat' : 'boxscore'}).a['href']
                        links = links.append({'Date' : date, 'URL' : box_url}, ignore_index=True)
                        
    return links.drop_duplicates()

def get_box_scores(links):
    """ 
    Scrapes box scores from set of provided links.
  
    This function iterates through the links provided and scrapes the corresponding box scores.
  
    Parameters: 
    links (DataFrame) : DataFrame with two columns, "Date" and "URL"
    Returns: 
    List of boxscore objects for all the requested games.

    """

    box_scores = []
    for row in links.itertuples(index=False):
        time.sleep(2)
        print('Scraping ' + row[1], end='\r')
        scraper = BoxScoreScraper(row[1])
        scraper.scrape_box_score()
        box_scores.append(scraper.box_score)

    return box_scores


def parse_box_scores(scores):
    """ 
    Converts list of boxscore objects into aggregate datasets.
  
    This function iterates through the link os Box Scores provided and outputs [insert].
  
    Parameters: 
    scores (List of BoxScore object) : List of boxscores to be included in output datasets.

    Returns: 
    DataFrames of game-by-game, game-level, batter-level, pitcher-level data.
    """

    # Predefine output dataframes
    game_level = pd.DataFrame(columns=['GameID', 'AwayTeam', 'HomeTeam', 'DateTime' , 'Attendance', 'Venue', 'Duration', 'Details',
                                        'AwayScore', 'HomeScore'])

    team_level = pd.DataFrame(columns=['GameID', 'Team', 'HomeAway', 'Inn1', 'Inn2', 'Inn3', 'Inn4', 'Inn5', 'Inn6', 'Inn7', 'Inn8', 'Inn9', 
                                        'Runs', 'Hits', 'Errors', 'AB', 'R', 'H', 'RBI', 'BB', 'SO', 'PA', 'BA', 'OBP', 'SLG', 'OPS', 'Pit', 'Str', 'WPA', 'aLI', 'WPA+', 'WPA-', 'RE24', 'PO', 'A',
                                        'Starter', 'IP', 'H_P', 'R_P', 'ER', 'BB_P', 'SO_P', 'HR_P', 'ERA', 'BF', 'Pit_P', 'Str_P', 'Ctct', 'StS', 'StL', 'GB', 'FB', 'LD', 'Unk', 'GSc', 'IR', 'IS', 'WPA_P', 'aLI_P', 'RE24_P'])

    batter_level = pd.DataFrame(columns=['GameID', 'Player', 'Team', 'HomeAway', 'Position', 'AB', 'R', 'H', 'RBI', 'BB', 'SO', 'PA', 'BA',                                             'OBP', 'SLG', 'OPS', 'Pit', 'Str', 'WPA', 'aLI', 'WPA+', 'WPA-', 'RE24', 'PO', 'A', 'Details'])

    pitcher_level = pd.DataFrame(columns=['GameID', 'Player', 'Team', 'HomeAway', 'Starter', 'Details', 'IP', 'H', 'R', 'ER', 'BB', 'SO', 'HR',                                        'ERA', 'BF', 'Pit', 'Str', 'Ctct', 'StS', 'StL', 'GB', 'FB', 'LD', 'Unk', 'GSc', 'IR', 'IS', 'WPA',
                                            'aLI', 'RE24'])

    # Iterate through all box scores
    for i, box_score in enumerate(scores):    

        # Generate unique game id
        game_id = hash(box_score.away_team + box_score.home_team + str(box_score.date) + str(box_score.time))

        # Convert date and time to datetime object if it exists
        
        if isinstance(box_score.time, str):
            new_datetime = dateparser.parse(box_score.date + ' ' + box_score.time)
        else:
            new_datetime = dateparser.parse(box_score.date + ' 11:59 pm')
        
        # Populate row of game level dataframe
        linescore = box_score.linescore
        game_level = game_level.append({'GameID' : game_id,
                            'AwayTeam' : box_score.away_team,
                            'HomeTeam' : box_score.home_team,
                            'DateTime' : new_datetime,
                            'Attendance' : box_score.attendance,
                            'Venue' : box_score.venue,
                            'Duration' : box_score.duration,
                            'Details' : box_score.time_place,
                            'AwayScore' : linescore.loc[0, 'R'],
                            'HomeScore' : linescore.loc[1, 'R']}, ignore_index=True)

        # Populate team level dataframes
        team_level = team_level.append({'GameID' : game_id,
                                    'Team' : box_score.away_team,
                                    'HomeAway' : 'Away',
                                    'Inn1' : (linescore.loc[0, '1'] if '1' in linescore.columns else np.nan),
                                    'Inn2' : (linescore.loc[0, '2'] if '2' in linescore.columns else np.nan),
                                    'Inn3' : (linescore.loc[0, '3'] if '3' in linescore.columns else np.nan),
                                    'Inn4' : (linescore.loc[0, '4'] if '4' in linescore.columns else np.nan),
                                    'Inn5' : (linescore.loc[0, '5'] if '5' in linescore.columns else np.nan),
                                    'Inn6' : (linescore.loc[0, '6'] if '6' in linescore.columns else np.nan),
                                    'Inn7' : (linescore.loc[0, '7'] if '7' in linescore.columns else np.nan),
                                    'Inn8' : (linescore.loc[0, '8'] if '8' in linescore.columns else np.nan),
                                    'Inn9' : (linescore.loc[0, '9'] if '9' in linescore.columns else np.nan),
                                    'Runs' : linescore.loc[0, 'R'],
                                    'Hits' : linescore.loc[0, 'H'],
                                    'Errors' : linescore.loc[0, 'E'],
                                    'AB' : box_score.away_batting.iloc[-1]['AB'], 
                                    'R' : box_score.away_batting.iloc[-1]['R'], 
                                    'RBI' : box_score.away_batting.iloc[-1]['RBI'], 
                                    'BB': box_score.away_batting.iloc[-1]['BB'], 
                                    'SO' : box_score.away_batting.iloc[-1]['SO'], 
                                    'PA' : box_score.away_batting.iloc[-1]['PA'], 
                                    'BA' : box_score.away_batting.iloc[-1]['BA'],
                                    'OBP' : box_score.away_batting.iloc[-1]['OBP'], 
                                    'SLG' : box_score.away_batting.iloc[-1]['SLG'], 
                                    'OPS' : box_score.away_batting.iloc[-1]['OPS'], 
                                    'Pit' : box_score.away_batting.iloc[-1]['Pit'], 
                                    'Str' : box_score.away_batting.iloc[-1]['Str'], 
                                    'WPA' : box_score.away_batting.iloc[-1]['WPA'], 
                                    'aLI' : box_score.away_batting.iloc[-1]['aLI'], 
                                    'WPA+' : box_score.away_batting.iloc[-1]['WPA+'], 
                                    'WPA-' : box_score.away_batting.iloc[-1]['WPA-'], 
                                    'RE24' : box_score.away_batting.iloc[-1]['RE24'],
                                    'PO' : box_score.away_batting.iloc[-1]['PO'],
                                    'A' : box_score.away_batting.iloc[-1]['A'],
                                    'Starter' : box_score.away_pitching.iloc[0, 0],
                                    'IP' : box_score.away_pitching.iloc[-1]['IP'], 
                                    'H_P' : box_score.away_pitching.iloc[-1]['H'], 
                                    'R_P' : box_score.away_pitching.iloc[-1]['R'], 
                                    'ER' : box_score.away_pitching.iloc[-1]['ER'], 
                                    'BB_P' : box_score.away_pitching.iloc[-1]['BB'], 
                                    'SO_P' : box_score.away_pitching.iloc[-1]['SO'], 
                                    'HR_P' : box_score.away_pitching.iloc[-1]['HR'], 
                                    'ERA' : box_score.away_pitching.iloc[-1]['ERA'],
                                    'BF' : box_score.away_pitching.iloc[-1]['BF'], 
                                    'Pit_P' : box_score.away_pitching.iloc[-1]['Pit'], 
                                    'Str_P' : box_score.away_pitching.iloc[-1]['Str'], 
                                    'Ctct' : box_score.away_pitching.iloc[-1]['Ctct'], 
                                    'StS' : box_score.away_pitching.iloc[-1]['StS'], 
                                    'StL' : box_score.away_pitching.iloc[-1]['StL'] , 
                                    'GB' : box_score.away_pitching.iloc[-1]['GB'], 
                                    'FB' : box_score.away_pitching.iloc[-1]['FB'], 
                                    'LD' : box_score.away_pitching.iloc[-1]['LD'], 
                                    'Unk' : box_score.away_pitching.iloc[-1]['Unk'],
                                    'GSc' : box_score.away_pitching.iloc[-1]['GSc'], 
                                    'IR' : box_score.away_pitching.iloc[-1]['IR'], 
                                    'IS' : box_score.away_pitching.iloc[-1]['IS'], 
                                    'WPA_P' : box_score.away_pitching.iloc[-1]['WPA'], 
                                    'aLI_P' : box_score.away_pitching.iloc[-1]['aLI'], 
                                    'RE24_P' : box_score.away_pitching.iloc[-1]['RE24']}, ignore_index=True)
        
        team_level = team_level.append({'GameID' : game_id,
                                    'Team' : box_score.home_team,
                                    'HomeAway' : 'Home',
                                    'Inn1' : (linescore.loc[1, '1'] if '1' in linescore.columns else np.nan),
                                    'Inn2' : (linescore.loc[1, '2'] if '2' in linescore.columns else np.nan),
                                    'Inn3' : (linescore.loc[1, '3'] if '3' in linescore.columns else np.nan),
                                    'Inn4' : (linescore.loc[1, '4'] if '4' in linescore.columns else np.nan),
                                    'Inn5' : (linescore.loc[1, '5'] if '5' in linescore.columns else np.nan),
                                    'Inn6' : (linescore.loc[1, '6'] if '6' in linescore.columns else np.nan),
                                    'Inn7' : (linescore.loc[1, '7'] if '7' in linescore.columns else np.nan),
                                    'Inn8' : (linescore.loc[1, '8'] if '8' in linescore.columns else np.nan),
                                    'Inn9' : (linescore.loc[1, '9'] if '9' in linescore.columns else np.nan),
                                    'Runs' : linescore.loc[1, 'R'],
                                    'Hits' : linescore.loc[1, 'H'],
                                    'Errors' : linescore.loc[1, 'E'],
                                    'AB' : box_score.home_batting.iloc[-1]['AB'], 
                                    'R' : box_score.home_batting.iloc[-1]['R'], 
                                    'RBI' : box_score.home_batting.iloc[-1]['RBI'], 
                                    'BB': box_score.home_batting.iloc[-1]['BB'], 
                                    'SO' : box_score.home_batting.iloc[-1]['SO'], 
                                    'PA' : box_score.home_batting.iloc[-1]['PA'], 
                                    'BA' : box_score.home_batting.iloc[-1]['BA'],
                                    'OBP' : box_score.home_batting.iloc[-1]['OBP'], 
                                    'SLG' : box_score.home_batting.iloc[-1]['SLG'], 
                                    'OPS' : box_score.home_batting.iloc[-1]['OPS'], 
                                    'Pit' : box_score.home_batting.iloc[-1]['Pit'], 
                                    'Str' : box_score.home_batting.iloc[-1]['Str'], 
                                    'WPA' : box_score.home_batting.iloc[-1]['WPA'], 
                                    'aLI' : box_score.home_batting.iloc[-1]['aLI'], 
                                    'WPA+' : box_score.home_batting.iloc[-1]['WPA+'], 
                                    'WPA-' : box_score.home_batting.iloc[-1]['WPA-'], 
                                    'RE24' : box_score.home_batting.iloc[-1]['RE24'],
                                    'PO' : box_score.home_batting.iloc[-1]['PO'],
                                    'A' : box_score.home_batting.iloc[-1]['A'],
                                    'Starter' : box_score.home_pitching.iloc[0, 0],
                                    'IP' : box_score.home_pitching.iloc[-1]['IP'], 
                                    'H_P' : box_score.home_pitching.iloc[-1]['H'], 
                                    'R_P' : box_score.home_pitching.iloc[-1]['R'], 
                                    'ER' : box_score.home_pitching.iloc[-1]['ER'], 
                                    'BB_P' : box_score.home_pitching.iloc[-1]['BB'], 
                                    'SO_P' : box_score.home_pitching.iloc[-1]['SO'], 
                                    'HR_P' : box_score.home_pitching.iloc[-1]['HR'], 
                                    'ERA' : box_score.home_pitching.iloc[-1]['ERA'],
                                    'BF' : box_score.home_pitching.iloc[-1]['BF'], 
                                    'Pit_P' : box_score.home_pitching.iloc[-1]['Pit'], 
                                    'Str_P' : box_score.home_pitching.iloc[-1]['Str'], 
                                    'Ctct' : box_score.home_pitching.iloc[-1]['Ctct'], 
                                    'StS' : box_score.home_pitching.iloc[-1]['StS'], 
                                    'StL' : box_score.home_pitching.iloc[-1]['StL'] , 
                                    'GB' : box_score.home_pitching.iloc[-1]['GB'], 
                                    'FB' : box_score.home_pitching.iloc[-1]['FB'], 
                                    'LD' : box_score.home_pitching.iloc[-1]['LD'], 
                                    'Unk' : box_score.home_pitching.iloc[-1]['Unk'],
                                    'GSc' : box_score.home_pitching.iloc[-1]['GSc'], 
                                    'IR' : box_score.home_pitching.iloc[-1]['IR'], 
                                    'IS' : box_score.home_pitching.iloc[-1]['IS'], 
                                    'WPA_P' : box_score.home_pitching.iloc[-1]['WPA'], 
                                    'aLI_P' : box_score.home_pitching.iloc[-1]['aLI'], 
                                    'RE24_P' : box_score.home_pitching.iloc[-1]['RE24']}, ignore_index=True)


        # Populate batter level dataframes
        away_batting_df = box_score.away_batting.iloc[:-1]
        away_batting_df.insert(0, 'GameID', game_id)
        away_batting_df.insert(2, 'Team', box_score.away_team)
        away_batting_df.insert(3, 'HomeAway', 'Away')
        batter_level = batter_level.append(away_batting_df, ignore_index=True)

        home_batting_df = box_score.home_batting.iloc[:-1]
        home_batting_df.insert(0, 'GameID', game_id)
        home_batting_df.insert(2, 'Team', box_score.home_team)
        home_batting_df.insert(3, 'HomeAway', 'Home')
        batter_level = batter_level.append(home_batting_df, ignore_index=True)

        # Populate batter level dataframe
        away_pitch_df = box_score.away_pitching.iloc[:-1]
        away_pitch_df.insert(0, 'GameID', game_id)
        away_pitch_df.insert(2, 'Team', box_score.away_team)
        away_pitch_df.insert(3, 'HomeAway', 'Away')
        away_pitch_df.insert(4, 'Starter', box_score.away_pitching['Player'][0])
        pitcher_level = pitcher_level.append(away_pitch_df, ignore_index=True)

        home_pitch_df = box_score.home_pitching.iloc[:-1]
        home_pitch_df.insert(0, 'GameID', game_id)
        home_pitch_df.insert(2, 'Team', box_score.home_team)
        home_pitch_df.insert(3, 'HomeAway', 'Home')
        home_pitch_df.insert(4, 'Starter', box_score.home_pitching['Player'][0])
        pitcher_level = pitcher_level.append(home_pitch_df, ignore_index=True)

    out = {'Game' : game_level,
            'Team' : team_level,
            'Batter' : batter_level,
            'Pitcher' : pitcher_level}
    return out