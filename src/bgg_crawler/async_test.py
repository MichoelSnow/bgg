import aiohttp
import asyncio
import uvloop
from bs4 import BeautifulSoup
import requests
import re
import json
from requests.compat import urljoin
from colorama import Fore
from datetime import datetime

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

loop = asyncio.get_event_loop()


def game_data_sync():
    xml_bs = 'https://www.boardgamegeek.com/xmlapi2/thing?type=boardgame&stats=1&ratingcomments=1&page=1&pagesize=10&id='
    all_items = []
    t0 = datetime.now()
    for pg in range(1, 3):
        soup_pg = browse_games(pg)
        pg_ids, pg_links = extract_game_ids(soup_pg)
        xml_fl = requests.get(f'{xml_bs}{",".join(pg_ids)}')
        soup_xml = BeautifulSoup(xml_fl.content, 'xml')
        t1 = datetime.now()
        all_items += extract_xml(soup_xml, pg_links)
        dt1 = datetime.now() - t1
        print(Fore.YELLOW + "total time: {:,.2f} sec.".format(dt1.total_seconds()), flush=True)
        print(Fore.WHITE + f"Page {pg} extracted", flush=True)
    dt = datetime.now() - t0
    print(Fore.YELLOW +  "total time: {:,.2f} sec.".format(dt.total_seconds()), flush=True)
    print(5)
    return all_items


def extract_xml(soup, game_links):
    item_list = []
    items = soup.find_all('item')
    t1 = datetime.now()
    for idx, item in enumerate(items):
        item_list.append(extract_item(item, game_links[idx]))
    dt1 = datetime.now() - t1
    print(Fore.YELLOW + "total time: {:,.2f} sec.".format(dt1.total_seconds()), flush=True)
    return item_list


def extract_item(game_item, game_url):
    game_dict = {'name': game_item.find('name')['value'],
                 'game_id': game_item['id'],
                 'url': game_url}
    values_int = ['yearpublished', 'minplayers', 'maxplayers', 'playingtime', 'minplaytime', 'maxplaytime', 'minage']
    for vals in values_int:
        game_dict[vals] = game_item.find(vals)['value']
    game_dict['numplayers'] = {}
    for plyrs in game_item.find_all('results', {'numplayers': re.compile('\d')}):
        game_dict['numplayers'][plyrs['numplayers']] = {x['value']: int(x['numvotes']) for x in
                                                        plyrs.find_all('result')}
    link_categ = ['boardgamecategory', 'boardgamemechanic', 'boardgamefamily', 'boardgameexpansion', 'boardgameartist',
                  'boardgamecompilation', 'boardgameimplementation', 'boardgamedesigner', 'boardgamepublisher',
                  'boardgameintegration']
    for categ in link_categ:
        game_dict[categ] = [x['value'] for x in game_item.find_all('link', {'type': categ})]
    stats_float = ['usersrated', 'average', 'bayesaverage', 'stddev', 'median', 'averageweight']
    for stat in stats_float:
        game_dict[stat] = float(game_item.find(stat)['value'])
    stats_int = ['owned', 'trading', 'wanting', 'wishing', 'numcomments', 'numweights']
    for stat in stats_int:
        game_dict[stat] = int(game_item.find(stat)['value'])
    game_dict['ranks'] = {x['friendlyname']: int(x['value']) for x in game_item.find_all('rank')}
    game_dict['rank_bayes'] = {x['friendlyname']: float(x['bayesaverage']) for x in game_item.find_all('rank')}
    return game_dict


def browse_games(page_num):
    bs_url = 'https://boardgamegeek.com/browse/boardgame/page/'
    pg_url = f'{bs_url}{page_num}'
    pg = requests.get(pg_url)
    soup = BeautifulSoup(pg.content, 'html.parser')
    return soup


def extract_game_ids(soup):
    bs_pg = 'https://boardgamegeek.com/'
    all_games = soup.find_all('td', {'class': 'collection_objectname'})
    game_ids = [x.find('a')['href'].split('/')[-2] for x in all_games]
    game_pages = [urljoin(bs_pg, x.find('a')['href']) for x in all_games]
    return game_ids, game_pages


if __name__ == '__main__':
    game_items = game_data_sync()
    print(5)
    # with open('../data/games_info.json', 'w') as fp:
    #     json.dump(game_items, fp)
