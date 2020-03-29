import json
# import requests
# import pandas as pd
from time import sleep
from datetime import datetime
import asyncio
from asyncio import AbstractEventLoop
import aiohttp


def main():
    try:
        with open('/home/msnow/git/bgg/src/data/bga_games_190511.json', 'r') as fp:
            games_list = json.load(fp)
    except:
        pass
        games_list = []
    loop = asyncio.get_event_loop()
    for i in range(len(games_list), 10000, 2000):
        games_list += loop.run_until_complete(get_game_data(loop, i))
        with open('/home/msnow/git/bgg/src/data/bga_games_190511.json', 'w') as fp:
            json.dump(games_list, fp)
        sleep(30)
    with open('/home/msnow/git/bgg/src/data/bga_games_190511.json', 'w') as fp:
        json.dump(games_list, fp)


async def get_game_data(loop: AbstractEventLoop, min_game: int) -> list:
    games_list = []
    games_json = []
    with open('/home/msnow/site_configs/secrets.json', 'r') as fp:
        secrets = json.load(fp)
    client_id = secrets['board_game_atlas']['client_id']
    for game_skip in range(min_game, min_game + 2000, 100):
        games_json.append((loop.create_task(get_json(game_skip, client_id)), game_skip))

    for pg, n in games_json:
        pg_json = await pg
        games_list += pg_json['games']
        print(n, str(datetime.now().time())[:12], flush=True)

    return games_list


async def get_json(game_skip: int, client_id: str):
    json_url = f'https://www.boardgameatlas.com/api/search?skip={game_skip}&pretty=true&limit=100&client_id={client_id}'
    connector = aiohttp.TCPConnector(limit_per_host=5)
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get(json_url) as resp:
            resp.raise_for_status()

            json_resp = await resp.json()
            return json_resp


if __name__ == '__main__':
    main()
