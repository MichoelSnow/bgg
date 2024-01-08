from bs4 import BeautifulSoup
import requests
import json
import math
from time import sleep
import os

def ratings_data(games_dict):
    pg_sz = 100
    xml_bs = f'https://www.boardgamegeek.com/xmlapi2/thing?type=boardgame&ratingcomments=1&pagesize={pg_sz}'
    ratings_list = [(x['game_id'], x['usersrated']) for x in games_dict]
    # ratings_list = ratings_list[:10]
    # ratings_list = ['220308', '182028', '187645', '193738']
    ratings_list.sort(key=lambda tup: tup[1], reverse=False)
    # ratings_list = ratings_list[500:504]
    group_sz = 50
    rating_dict = {}
    comment_dict = {}
    for group_num in range(math.ceil(len(ratings_list) / group_sz)):
        group_ids = ratings_list[group_num * group_sz:(group_num + 1) * group_sz]
        pg_ct = math.ceil(group_ids[0][1] / pg_sz)
        # rat_ct = 0
        for pg_num in range(1, pg_ct + 1):
            xml_ids = ','.join([x[0] for x in group_ids if x[1] > (pg_num - 1) * pg_sz])
            xml_fl = requests.get(f'{xml_bs}&page={pg_num}&id={xml_ids}')
            while xml_fl.status_code !=200:
                if xml_fl.status_code == 429:
                    sleep(1)
                else:
                    sleep(1)
            soup_xml = BeautifulSoup(xml_fl.content, 'xml')
            rating_dict, comment_dict = extract_ratings(soup_xml, rating_dict, comment_dict)
        # print(5)
        with open('../data/game_ratings_tmp.json', 'w') as fp:
            json.dump(rating_dict, fp)
        with open('../data/game_comments_tmp.json', 'w') as fp:
            json.dump(comment_dict, fp)
        with open('../data/game_ratings_tmp2.json', 'w') as fp:
            json.dump(rating_dict, fp)
        with open('../data/game_comments_tmp2.json', 'w') as fp:
            json.dump(comment_dict, fp)
        print(f'{len(rating_dict)} games done')
    return rating_dict, comment_dict


def extract_ratings(soup, ratings, comments):
    items = soup.find_all('item')
    for item in items:
        if item['id'] not in ratings:
            ratings[item['id']] = {}
        xml_rat = item.find_all('comment')
        for rat in xml_rat:
            rat_val = rat['rating']
            if rat_val not in ratings[item['id']]:
                ratings[item['id']][rat_val] = [rat['username']]
            else:
                ratings[item['id']][rat_val].append(rat['username'])
            if rat['value']:
                if rat_val not in comments:
                    comments[rat_val] = [rat['value']]
                else:
                    comments[rat_val].append(rat['value'])
    # rat_ct = sum(len(ratings['56692'][x]) for x in ratings['56692'].keys())
    # print(rat_ct, '+100')
    # if rat_ct == old_rat:
    #     print(5)
    #     print(4)
    # print(5)
    return ratings, comments#, rat_ct


if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.realpath(__file__))
    data_dir = os.path.join(current_dir, os.pardir, "data")
    with open(os.path.join(data_dir,'games_info.json'), 'r') as fp:
        game_info_dict = json.load(fp)
    all_ratings, all_comments = ratings_data(game_info_dict)
    print(5)
    with open(os.path.join(data_dir,'games_ratings.json'), 'w') as fp:
        json.dump(all_ratings, fp)
    with open(os.path.join(data_dir,'game_comments.json'), 'w') as fp:
        json.dump(all_comments, fp)
