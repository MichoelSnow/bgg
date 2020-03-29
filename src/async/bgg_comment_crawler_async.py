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
import math


def main():
    # Create loop
    print(str(datetime.now().time())[:8])
    loop = asyncio.get_event_loop()
    user_rating, user_comment = loop.run_until_complete(get_game_ratings(loop))
    with open('../data/user_ratings_190508.json', 'w') as fp:
        json.dump(user_rating, fp)
    with open('../data/user_comments_190508.json', 'w') as fp:
        json.dump(user_comment, fp)


async def get_game_ratings(loop: AbstractEventLoop):
    with open('../data/game_info_190508.json', 'r') as fp:
        games_dict = json.load(fp)
    pg_sz = 100
    xml_bs = f'https://www.boardgamegeek.com/xmlapi2/thing?type=boardgame&ratingcomments=1&pagesize={pg_sz}'
    ratings_list = [(x['game_id'], x['usersrated']) for x in games_dict]
    ratings_list.sort(key=lambda tup: tup[1], reverse=False)
    group_sz = 50
    user_rating = []
    user_comment = []
    group_xml = []
    for group_num in range(math.ceil(len(ratings_list) / group_sz)):
        group_ids = ratings_list[group_num * group_sz:(group_num + 1) * group_sz]
        pg_ct = math.ceil(group_ids[0][1] / pg_sz)
        # group_xml[group_num] = []
        for pg_num in range(1, pg_ct + 1):
            xml_ids = ','.join([x[0] for x in group_ids if x[1] > (pg_num - 1) * pg_sz])
            xml_url = f'{xml_bs}&page={pg_num}&id={xml_ids}'
            group_xml.append((loop.create_task(get_xml(xml_url)), pg_num))
        # break
    for pg_xml, n in group_xml:
        xml = await pg_xml
        user_rating, user_comment = get_pg_ratings(xml, user_rating, user_comment)
        print(f'group {n} at {(str(datetime.now().time())[:8])}', flush=True)

    print(5)

    print(str(datetime.now().time())[:8])
    return user_rating, user_comment


async def get_xml(xml_pg_url):
    connector = aiohttp.TCPConnector(limit_per_host=2)
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get(xml_pg_url) as resp:
            resp.raise_for_status()

            xml = await resp.text()
            return xml


def get_pg_ratings(html: str, user_ratings: list, user_comments: list):
    # print(Fore.CYAN + f"Getting ids for page number {page_number}", flush=True)
    soup = BeautifulSoup(html, 'xml')
    items = soup.find_all('item')
    for item in items:
        # item_dict = defaultdict(dict)
        rating_list = [x for x in item.comments.contents if type(x) == bs4.element.Tag]
        comment_list = [x for x in rating_list if x['value'] != '']
        for rating in rating_list:
            user_ratings.append({'user':rating['username'],
                                 'rating': float(rating['rating']),
                                 'game_id': item['id']})
            # ratings_dict[item['id']].update({rating['username']: float(rating['rating'])})
            # users_dict[rating['username']].update({item['id']: float(rating['rating'])})
        for comment in comment_list:
            user_comments.append({'user': comment['username'],
                                 'rating': float(comment['rating']),
                                 'game_id': item['id'],
                                  'comment': comment['value']})
            # item_dict[float(comment['rating'])].update({comment['username']: comment['value']})
            # comments_dict[item['id']].update({comment['username']: [comment['value'], float(comment['rating'])]})
    return user_ratings, user_comments


if __name__ == '__main__':
    main()
    # game_items = game_data_async()
    # export_csv(game_items)
    # print(5)
