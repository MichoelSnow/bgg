from bs4 import BeautifulSoup
import requests
import pandas as pd
import json
from requests.compat import urljoin
from datetime import datetime
import re
import asyncio
from asyncio import AbstractEventLoop
import aiohttp
from colorama import Fore
from collections import defaultdict
import bs4
from unidecode import unidecode
from time import sleep


def main():
    # Create loop
    print(str(datetime.now().time())[:8])
    loop = asyncio.get_event_loop()
    try:
        with open('../data/game_info_190509.json', 'r') as fp:
            xml_data = json.load(fp)
    except:
        pass
        xml_data = []
    pg_rng = 20
    for i in range(int(len(xml_data) / 100) + 1, 151, pg_rng):
        xml_data += loop.run_until_complete(get_game_ids(loop, i, i + pg_rng))
        with open('../data/game_info_190509.json', 'w') as fp:
            json.dump(xml_data, fp)
        sleep(60)


async def get_game_ids(loop: AbstractEventLoop, start_pg: int, end_pg: int) -> list:
    pg_html = []
    pg_ids = []
    pg_urls = []
    xml_data = []
    for pg_rng in range(start_pg, end_pg):
        pg_html.append((loop.create_task(get_html(pg_rng)), pg_rng))

    pg_xml = []
    for pg, n in pg_html:
        html = await pg
        # print(Fore.GREEN + f"Starting HTML for page {n} at time {str(datetime.now().time())[:8]}", flush=True)
        pg_data = get_pg_ids(html)
        print(Fore.LIGHTGREEN_EX + f"Finished HTML for page {n} at time {str(datetime.now().time())[:8]}", flush=True)
        pg_ids += pg_data[0]
        pg_urls += pg_data[1]
        pg_xml.append((loop.create_task(get_xml(pg_data[0])), n))

    for pg_xml_data, n in pg_xml:
        xml = await pg_xml_data
        print(Fore.BLUE + f"Starting XML page {n} at time {str(datetime.now().time())[:8]}", flush=True)
        xml_data += extract_xml(xml)
        print(Fore.LIGHTBLUE_EX + f"Finished XML page {n} at time {str(datetime.now().time())[:8]}", flush=True)

    for idx, game_url in enumerate(pg_urls):
        xml_data[idx]['url'] = game_url
    print(str(datetime.now().time())[:8])

    return xml_data


async def get_html(pg_num: int):
    # print(Fore.YELLOW + f"Getting HTML for page number {pg_num}", flush=True)
    bs_url = 'https://boardgamegeek.com/browse/boardgame/page/'
    connector = aiohttp.TCPConnector(limit_per_host=2)
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get(f'{bs_url}{pg_num}') as resp:
            resp.raise_for_status()

            html = await resp.text()
            return html


async def get_xml(pg_ids):
    xml_bs = 'https://www.boardgamegeek.com/xmlapi2/thing?type=boardgame&stats=1&ratingcomments=1&page=1&pagesize=10&id='
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{xml_bs}{",".join(pg_ids)}') as resp:
            resp.raise_for_status()

            xml = await resp.text()
            return xml


def get_pg_ids(html: str):
    # print(Fore.CYAN + f"Getting ids for page number {page_number}", flush=True)
    soup = BeautifulSoup(html, 'html.parser')
    bs_pg = 'https://boardgamegeek.com/'
    all_games = soup.find_all('td', {'class': 'collection_objectname'})
    game_ids = [x.find('a')['href'].split('/')[-2] for x in all_games]
    game_pages = [urljoin(bs_pg, x.find('a')['href']) for x in all_games]
    return game_ids, game_pages


def extract_xml(xml: str):
    item_list = []
    soup = BeautifulSoup(xml, "xml")
    items = soup.find_all('item')
    for idx, item in enumerate(items):
        item_list.append(extract_item_dict(item))
    return item_list


def extract_item_dict(game_item):
    item_dict = defaultdict(list)
    for x in range(len(game_item.contents)):
        if type(game_item.contents[x]) == bs4.element.Tag:
            itm = game_item.contents[x]
            item_dict[itm.name].append(itm.attrs)
    game_dict = {'name': item_dict['name'][0]['value'],
                 'game_id': game_item['id']}
    values_int = ['yearpublished', 'minplayers', 'maxplayers', 'playingtime', 'minplaytime', 'maxplaytime', 'minage']
    for vals in values_int:
        game_dict[vals] = item_dict[vals][0]['value']
    link_categ = ['boardgamecategory', 'boardgamemechanic', 'boardgamefamily', 'boardgameexpansion', 'boardgameartist',
                  'boardgamecompilation', 'boardgameimplementation', 'boardgamedesigner', 'boardgamepublisher',
                  'boardgameintegration']
    link_dict = defaultdict(list)
    for item_link in item_dict['link']:
        link_dict[item_link['type']].append(unidecode(item_link['value']))
    for categ in link_categ:
        game_dict[categ] = link_dict[categ]
    stats_float = ['average', 'bayesaverage', 'stddev', 'median', 'averageweight']
    for stat in stats_float:
        game_dict[stat] = float(eval(f'game_item.ratings.{stat}["value"]'))
    stats_int = ['usersrated', 'owned', 'trading', 'wanting', 'wishing', 'numcomments', 'numweights']
    for stat in stats_int:
        game_dict[stat] = int(eval(f'game_item.ratings.{stat}["value"]'))
    game_ranks = [x for x in game_item.ranks.contents if type(x) == bs4.element.Tag]
    for rnk in game_ranks:
        game_dict[rnk['friendlyname'].replace(' ', '')] = int(rnk['value'])
    return game_dict


if __name__ == '__main__':
    main()
    # game_items = game_data_async()
    # export_csv(game_items)
    # print(5)
