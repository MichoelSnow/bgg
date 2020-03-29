import pandas as pd
import os


def append_ratings(fl_path: str, orig_data: str, new_data: str):
    df_rank = pd.read_csv(os.path.join(fl_path, 'curated', orig_data))
    df_tmp = pd.read_csv(os.path.join(fl_path, new_data), usecols=['name', 'BoardGameRank'])
    df_tmp = df_tmp.rename(columns={'name': new_data[:10]})
    df_rank = df_rank.merge(right=df_tmp, how='left', on='BoardGameRank')
    df_rank.to_csv(os.path.join(fl_path, f'weekly_rankings_{new_data[:10]}.csv'), index=False)
    df_rank.to_csv(os.path.join(fl_path, 'curated', orig_data), index=False)


def newest_crawled(fl_path: str):
    fl_list = [x for x in os.listdir(fl_path) if x.endswith('.csv') and x.find('bgg_top') > 0]
    return fl_list[0]


if __name__ == '__main__':
    data_fl_path = '/home/msnow/git/bgg/data/kaggle/'
    rank_data = 'weekly_rankings.csv'
    new_week_data = newest_crawled(data_fl_path)
    append_ratings(data_fl_path, rank_data, new_week_data)
