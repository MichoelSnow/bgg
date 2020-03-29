import json


def combine(info_json, rating_json):
    game_info_rat = []
    for gm in info_json:
        gm['ratings'] = {}
        rat_sim_dict = {x: 0 for x in range(11)}
        rat_list = []
        # rat_sim_dict = {}
        for gm_scor in rating_json[gm['game_id']].keys():
            rat_list.append((float(gm_scor), len(rating_json[gm['game_id']][gm_scor])))
            rat_sim_dict[round(float(gm_scor))] += len(rating_json[gm['game_id']][gm_scor])
            # rat_sim_list.append((round(float(gm_scor)), len(rating_json[gm['game_id']][gm_scor])))
        gm['ratings'] = rat_list
        gm['ratings_simple'] = [(i,x) for i,x in rat_sim_dict.items()]
        gm['usersrated'] = int(gm['usersrated'])
        game_info_rat.append(gm)
    return game_info_rat

# def combine(info_json, rating_json):
#     game_info_rat = []
#     for gm in info_json:
#         gm['ratings'] = {}
#         gm['ratings_simple'] = {x: 0 for x in range(11)}
#         rat_list = []
#         rat_sim_list =
#         for gm_scor in rating_json[gm['game_id']].keys():
#             gm['ratings'][float(gm_scor)] = len(rating_json[gm['game_id']][gm_scor])
#             gm['ratings_simple'][round(float(gm_scor))] += len(rating_json[gm['game_id']][gm_scor])
#         game_info_rat.append(gm)
#     return game_info_rat



# def add_price(info_json):
#     bs_url = 'https://www.amazon.com/s/ref=nb_sb_noss_1?url=search-alias%3Dtoys-and-games&field-keywords='
#     for gm in info_json:
#         url_nm = gm['url'].split('/')[-1].replace('-','+')
#         pg = requests.get(f'{bs_url}{url_nm}')
#         soup = BeautifulSoup(pg.content, 'html.parser')
#         print(5)
#     pg_url = 'https://boardgamegeek.com/boardgame/174430/gloomhaven'
#     pg = requests.get(pg_url)


if __name__ == '__main__':
    with open('../../data/crawler/game_info.json', 'r') as fp:
        game_info = json.load(fp)
    with open('../../data/crawler/game_ratings.json', 'r') as fp:
        game_rat = json.load(fp)
    # info_price_dict = add_price(game_info)
    info_rat_dict = combine(game_info, game_rat)
    with open('../../data/crawler/game_info_rat.json', 'w') as fp:
        json.dump(info_rat_dict, fp)
