import json
import requests
# import pandas as pd
from time import sleep, time
from datetime import datetime

with open('/home/msnow/site_configs/secrets.json', 'r') as fp:
    secrets = json.load(fp)

client_id = secrets['board_game_atlas']['client_id']

games_list = []

print(str(datetime.now().time())[:12])
for game_skip in range(0, 10000, 100):
    bga_req = requests.get(
        f'https://www.boardgameatlas.com/api/search?skip={game_skip}&pretty=true&limit=100&client_id={client_id}&')
    games_json = bga_req.json()['games']
    games_list += games_json
    print(game_skip, str(datetime.now().time())[:12])

with open('/home/msnow/git/bgg/src/data/bga_games_190511.json', 'w') as fp:
    json.dump(games_list, fp)
