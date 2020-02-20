import sys
import pandas as pd
sys.path.append('/Users/efriedlander/Dropbox/SportsBetting/mlb-predict')
from src.data import bbref_scrape

def test_BoxScoreScraper():
    url = 'https://www.baseball-reference.com/boxes/BAL/BAL201606040.shtml'
    scraper = bbref_scrape.BoxScoreScraper(url)
    scraper.scrape_box_score()
    box_score = scraper.box_score


def compare_linescore(box_score):
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
    assert(df.equals(box_score.line_score))
