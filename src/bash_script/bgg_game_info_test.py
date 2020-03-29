from bs4 import BeautifulSoup
import requests
import re
import json
from requests.compat import urljoin


def game_data():
    xml_bs = 'https://www.boardgamegeek.com/xmlapi2/thing?type=boardgame&stats=1&ratingcomments=1&page=1&pagesize=10&id='
    all_items = []
    for pg in range(1, 2):
        soup_pg = browse_games(pg)
        game_names = extract_game_ids(soup_pg)
        with open('../../data/tmp/test_script.json', 'w') as fp:
            json.dump(game_names, fp)


def browse_games(page_num):
    bs_url = 'https://boardgamegeek.com/browse/boardgame/page/'
    pg_url = f'{bs_url}{page_num}'
    pg = requests.get(pg_url)
    soup = BeautifulSoup(pg.content, 'html.parser')
    return soup


def extract_game_ids(soup):
    all_games = soup.find_all('td', {'class': 'collection_objectname'})
    game_names = [x.find('a')['href'].split('/')[-1] for x in all_games]
    return game_names


if __name__ == '__main__':
    game_data()
    # print('finished getting all the games')

