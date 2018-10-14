from urllib import request
from bs4 import BeautifulSoup, Comment
import pandas as pd
from datetime import datetime
import json




def extract_gm_id(soup):
    rows = soup.find('div', {'id': 'collection'}).find_all('tr')[1:]
    id_list = []
    for row in rows:
        id_list.append(int(row.find_all('a')[1]['href'].split('/')[2]))
    return id_list

def top_2k_gms(pg_gm_rnks):
    gm_ids = []
    for pg_num in range(1,21):
        pg = request.urlopen(f'{pg_gm_rnks}{str(pg_num)}')
        soup = BeautifulSoup(pg, 'html.parser')
        gm_ids += extract_gm_id(soup)
    return gm_ids

def extract_game_item(item):
    gm_dict = {}
    field_int = ['yearpublished', 'minplayers', 'maxplayers', 'playingtime', 'minplaytime', 'maxplaytime', 'minage']
    field_categ = ['boardgamecategory', 'boardgamemechanic', 'boardgamefamily','boardgamedesigner', 'boardgameartist', 'boardgamepublisher']
    field_rank = [x['friendlyname'] for x in item.find_all('rank')]
    field_stats = ['usersrated', 'average', 'bayesaverage', 'stddev', 'median', 'owned', 'trading', 'wanting', 'wishing', 'numcomments', 'numweights', 'averageweight']
    gm_dict['name'] = item.find('name')['value']
    gm_dict['id'] = item['id']
    gm_dict['num_of_rankings'] = int(item.find('comments')['totalitems'])
    for i in field_int:
        field_val = item.find(i)
        if field_val is None:
            gm_dict[i] = -1
        else:
            gm_dict[i] = int(field_val['value'])
    for i in field_categ:
        gm_dict[i] = [x['value'] for x in item.find_all('link',{'type':i})]
    for i in field_rank:
        field_val = item.find('rank',{'friendlyname':i})
        if field_val is None or field_val['value'] == 'Not Ranked':
            gm_dict[i.replace(' ','')] = -1
        else:
            gm_dict[i.replace(' ','')] = int(field_val['value'])
    for i in field_stats:
        field_val = item.find(i)
        if field_val is None:
            gm_dict[i] = -1
        else:
            gm_dict[i] = float(field_val['value'])
    return gm_dict

def create_df_gm_ranks(gm_ids, bs_pg_gm):
    gm_list = []
    idx_split = 4
    idx_size = int(len(gm_ids)/idx_split)
    for i in range(idx_split):
        idx = str(gm_ids[i*idx_size:(i+1)*idx_size]).replace(' ','')[1:-1]   
        pg = request.urlopen(f'{bs_pg_gm}{str(idx)}')
        xsoup = BeautifulSoup(pg, 'xml')
        gm_list += [extract_game_item(x) for x in xsoup.find_all('item')]
    df = pd.DataFrame(gm_list)
    return df


pg_gm_rnks = 'https://boardgamegeek.com/browse/boardgame/page/'
gm_ids = top_2k_gms(pg_gm_rnks)
bs_pg = 'https://www.boardgamegeek.com/xmlapi2/'
bs_pg_gm = f'{bs_pg}thing?type=boardgame&stats=1&ratingcomments=1&page=1&pagesize=10&id='
df = create_df_gm_ranks(gm_ids, bs_pg_gm)
df.to_csv(f'../../data/kaggle/bgg_top{len(gm_ids)}_{str(datetime.now().date())}.csv', index=False)


