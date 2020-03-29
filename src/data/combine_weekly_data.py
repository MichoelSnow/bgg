import pandas as pd
import os
from typing import List, Tuple, Dict
from collections import defaultdict
from datetime import datetime
import json


def get_game_data_path() -> str:
    current_dir = os.path.dirname(os.path.realpath(__file__))
    data_dir = os.path.join(current_dir, os.pardir, os.pardir, "data", "kaggle")
    return data_dir


def get_game_data_list(path: str) -> List[str]:
    data_files = [
        x
        for x in os.listdir(path)
        if x.endswith("bgg_top2000.csv") or x.endswith("bgg_top5000.csv")
    ]
    data_files.sort()
    return [os.path.join(path, x) for x in data_files]


def get_curated_df(data_list: List) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df_ref = None
    df_rank_dict = defaultdict(list)
    df_rank_id_dict = defaultdict(list)
    column_dtypes = {
        "AbstractGameRank": float,
        "BoardGameRank": float,
        "Children'sGameRank": float,
        "CustomizableRank": float,
        "FamilyGameRank": float,
        "PartyGameRank": float,
        "StrategyGameRank": float,
        "ThematicRank": float,
        "WarGameRank": float,
        "id": str,
        "game_id": str,
    }
    rankings_list = [
        "AbstractGameRank",
        "BoardGameRank",
        "ChildrensGameRank",
        "CustomizableRank",
        "FamilyGameRank",
        "PartyGameRank",
        "StrategyGameRank",
        "ThematicRank",
        "WarGameRank",
    ]
    for data_fl in data_list:
        df_init = pd.read_csv(data_fl, dtype=column_dtypes)
        df_init = df_init.rename(
            columns={"Children'sGameRank": "ChildrensGameRank", "id": "game_id"}
        )
        df_init = df_init.drop_duplicates(subset="game_id")
        if df_init.duplicated("BoardGameRank").sum() > 0:
            df_init.BoardGameRank = list(range(1, df_init.shape[0] + 1))
        for col in rankings_list:
            df_init[col] = df_init[col].astype("Int64").astype("Int32")
        init_date = get_data_date(data_fl)
        df_rank_dict = get_game_rank_dict(
            df_init, init_date, df_rank_dict, rankings_list
        )
        df_rank_id_dict = get_game_id_rank_dict(
            df_init, init_date, df_rank_id_dict, rankings_list
        )
        if data_fl == data_list[-1]:
            df_ref = get_game_ref(df_init)
    df_game_rank = get_game_rank(df_rank_dict["BoardGameRank"])
    df_game_id_rank = get_game_id_rank(df_rank_id_dict["BoardGameRank"])
    for rank_name, rank_list in df_rank_dict.items():
        if rank_name == "BoardGameRank":
            df_tmp = get_first_date(rank_name, rank_list)
            df_ref = df_ref.merge(df_tmp, on="name", how="left")
        df_tmp = get_rank_range(rank_name, rank_list)
        df_ref = df_ref.merge(df_tmp, on="name", how="left")
    df_ref["bgg_url"] = "https://boardgamegeek.com/boardgame/" + df_ref.game_id
    return (df_game_rank, df_game_id_rank, df_ref)


def get_first_date(rank_str: str, df_list: list) -> pd.DataFrame:
    df = pd.concat(df_list, sort=False, ignore_index=True).drop(columns=rank_str)
    df = df.dropna().sort_values(["rank_date"])
    df_first_date = (
        df.groupby("name", sort=False, as_index=False)
        .first()
        .rename(columns={"rank_date": "first_date_in_ref"})
    )
    return df_first_date


def get_rank_range(rank_str: str, df_list: list) -> pd.DataFrame:
    df = pd.concat(df_list, sort=False, ignore_index=True)
    df = (
        df.dropna()
        .sort_values([rank_str, "rank_date"])
        .drop_duplicates(subset=["name", rank_str])
    )
    df_gb = df.groupby("name", sort=False, as_index=False)
    df_gb_min = df_gb.first().rename(
        columns={rank_str: f"{rank_str}_min", "rank_date": f"{rank_str}_min_date"}
    )
    df_gb_max = df_gb.last().rename(
        columns={rank_str: f"{rank_str}_max", "rank_date": f"{rank_str}_max_date"}
    )
    df_rank_range = df_gb_min.merge(df_gb_max, on="name", how="outer")
    return df_rank_range


def get_game_rank(df_list: list) -> pd.DataFrame:
    df_rank = df_list[0]
    df_rank = df_rank.rename(columns={"name": df_rank.rank_date.iloc[0]}).drop(
        columns="rank_date"
    )
    df_rank.BoardGameRank = df_rank.BoardGameRank.astype(str)
    for df_tmp in df_list[1:]:
        df_tmp = df_tmp.rename(columns={"name": df_tmp.rank_date.iloc[0]}).drop(
            columns="rank_date"
        )
        df_tmp.BoardGameRank = df_tmp.BoardGameRank.astype(str)
        df_rank = df_rank.merge(df_tmp, on="BoardGameRank", how="outer")
    return df_rank


def get_game_id_rank(df_list: list) -> pd.DataFrame:
    df_rank = df_list[0]
    df_rank = df_rank.rename(columns={"game_id": df_rank.rank_date.iloc[0]}).drop(
        columns="rank_date"
    )
    df_rank.BoardGameRank = df_rank.BoardGameRank.astype(str)
    for df_tmp in df_list[1:]:
        df_tmp = df_tmp.rename(columns={"game_id": df_tmp.rank_date.iloc[0]}).drop(
            columns="rank_date"
        )
        df_tmp.BoardGameRank = df_tmp.BoardGameRank.astype(str)
        df_rank = df_rank.merge(df_tmp, on="BoardGameRank", how="outer")
    return df_rank


def get_game_ref(df: pd.DataFrame) -> pd.DataFrame:
    col_list = [
        "game_id",
        "name",
        "boardgamedesigner",
        "boardgameartist",
        "yearpublished",
        "minplayers",
        "maxplayers",
        "minage",
        "playingtime",
        "minplaytime",
        "maxplaytime",
        "boardgamepublisher",
        "boardgamecategory",
        "boardgamefamily",
        "boardgamemechanic",
    ]
    df = df[col_list].copy()
    return df


def get_data_date(data_path: str) -> str:
    return data_path.split("/")[-1][:10]


def get_game_rank_dict(
    df: pd.DataFrame, data_date: str, rank_dict: dict, rank_list: List
) -> Dict:
    for rank_name in rank_list:
        df_tmp = df[[rank_name, "name"]].copy()
        df_tmp["rank_date"] = data_date
        # rank_dict[rank_name].append(df_tmp.rename(columns={"name": data_date}))
        rank_dict[rank_name].append(df_tmp)
    return rank_dict


def get_game_id_rank_dict(
    df: pd.DataFrame, data_date: str, rank_dict: dict, rank_list: List
) -> Dict:
    for rank_name in rank_list:
        df_tmp = df[[rank_name, "game_id"]].copy()
        df_tmp["rank_date"] = data_date
        # rank_dict[rank_name].append(df_tmp.rename(columns={"name": data_date}))
        rank_dict[rank_name].append(df_tmp)
    return rank_dict


def update_metadata(path: str) -> None:
    meta_path = os.path.join(path, "summary", "dataset-metadata.json")
    with open(meta_path, "r") as fp:
        meta_dict = json.load(fp)
    today = datetime.now().strftime("%Y-%m-%d")
    rank_dict = {
        "path": f"{today}_game_rankings.csv",
        "description": f"Board Game Geek top rankings by name from 2018-10-06 to {today}",
    }
    rank_id_dict = {
        "path": f"{today}_game_id_rankings.csv",
        "description": f"Board Game Geek top rankings by id from 2018-10-06 to {today}",
    }
    ref_dict = {
        "path": f"{today}_game_reference.csv",
        "description": "Board Game Geek game reference",
    }
    meta_dict["resources"] = [rank_dict, rank_id_dict, ref_dict]
    with open(meta_path, "w") as fp:
        json.dump(meta_dict, fp)


if __name__ == "__main__":
    game_data_path = get_game_data_path()
    game_data_list = get_game_data_list(game_data_path)
    df_game_rankings, df_game_id_rankings, df_game_reference = get_curated_df(
        game_data_list
    )
    today = datetime.now().strftime("%Y-%m-%d")
    df_game_rankings.to_csv(
        os.path.join(game_data_path, "summary", f"{today}_game_rankings.csv"),
        index=False,
    )
    df_game_id_rankings.to_csv(
        os.path.join(game_data_path, "summary", f"{today}_game_id_rankings.csv"),
        index=False,
    )
    df_game_reference.to_csv(
        os.path.join(game_data_path, "summary", f"{today}_game_reference.csv"),
        index=False,
    )
    update_metadata(game_data_path)
