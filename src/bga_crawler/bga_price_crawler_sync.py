import json
import requests
from time import sleep
from datetime import datetime

with open('/home/msnow/site_configs/secrets.json', 'r') as fp:
    secrets = json.load(fp)
client_id = secrets['board_game_atlas']['client_id']

with open('/home/msnow/git/bgg/src/data/bga_games_190511.json', 'r') as fp:
    games_list = json.load(fp)

game_ids = [x['id'] for x in games_list]
price_dict = {}

print(str(datetime.now().time())[:12])
for n, game_id in enumerate(game_ids):
    bga_req = requests.get(
        f'https://www.boardgameatlas.com/api/game/prices?game_id={game_id}&client_id={client_id}')
    prices_json = bga_req.json()
    price_dict[game_id] = {x['store_name']: x['price_text'] for x in prices_json['prices'] if x['country'] == 'US'}
    sleep(1)
    if n % 500 == 0 and n > 0:
        print(n, str(datetime.now().time())[:12])
        with open('/home/msnow/git/bgg/src/data/bga_prices_190511.json', 'w') as fp:
            json.dump(price_dict, fp)

with open('/home/msnow/git/bgg/src/data/bga_prices_190511.json', 'w') as fp:
    json.dump(price_dict, fp)
