import pymongo
import json


def insert_bgg_info(bgg_dict:list):
    db = pymongo.MongoClient()['bgg']['game_info']
    inserted_ids = db.insert_many(bgg_dict)




if __name__ == '__main__':
    with open('../../data/crawler/game_info_rat.json', 'r') as fp:
        bgg_json = json.load(fp)
    insert_bgg_info(bgg_json)