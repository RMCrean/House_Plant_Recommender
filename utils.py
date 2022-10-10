"""
Functions to support the main Dash application.

"""
from typing import Tuple, Union
import numpy as np
import pandas as pd


def recommend_plant(df: pd.DataFrame, plants_selected: Union[str, list], cosine_sim: np.ndarray) -> list:
    """
    Recommend the top 10 most similar plants to a single or multiple plants.
    Similarity determined by the cosine_similarity (pre-determined).

    In the case of multiple plants to search against, each plant is weighted equally.

    Parameters
    ----------
    df : pd.DataFrame
        TODO

    plants_selected: Union[str, list]
        String (for single plant) or list (for multiple plants) of plant name(s) to make
        recommendations on.

    cosine_sim: np.ndarray
        Cosine similarity matrix.

    Returns
    ----------
    list
        Top 6 most similar plants ordered by their scores.
    """

    # single plant to search.
    if isinstance(plants_selected, str):
        search_idx, total_scores = _plant_recommend_scores(
            df=df, plant_name=plants_selected, cosine_sim=cosine_sim)

        # remove the plant that was searched from the results
        total_scores.pop(search_idx)

    # multiple plants to search.
    else:
        search_idxs, results = [], []
        for plant in plants_selected:
            search_idx, result = _plant_recommend_scores(
                df=df,
                plant_name=plant,
                cosine_sim=cosine_sim)
            search_idxs.append(search_idx)
            results.append(result)

        # sum each score for each plant searched and make combined score of same format as single search.
        total_scores = {}
        for key in results[0].keys():

            score = 0
            for idx in range(len(results)):
                score += results[idx][key]

            total_scores.update({key: round(score, 4)})

        total_scores = {k: v for k, v in sorted(
            total_scores.items(), key=lambda item: item[1], reverse=True)}

        # remove the plant that was searched for from the results
        for search_idx in search_idxs:
            total_scores.pop(search_idx)

    # convert from index and score to Plant Name
    top_plants = []
    for idx, (k, v) in enumerate(total_scores.items()):
        if idx == 6:
            break
        top_plants.append(df.iloc[k]["Plant_Name"])

    return top_plants


def _plant_recommend_scores(df: pd.DataFrame, plant_name: str, cosine_sim: np.ndarray) -> Tuple[int, dict]:
    """
    Determine the recommendation scores for a single plant.
    All scores are returned, not only the top scores.

    Parameters
    ----------
    df : pd.DataFrame
        TODO


    plant_name: str
        Name of the plant to search for similar plants.

    cosine_sim: np.ndarray
        Cosine similarity matrix.

    Returns
    ----------
    int
        Index of the plant that is being searched.

    dict
        Keys are the plant index and values are their score.
    """
    search_idx = df.loc[df["Plant_Name"] == plant_name].index[0]

    similarity_scores = pd.Series(
        cosine_sim[search_idx]).sort_values(ascending=False)
    idxs = list(similarity_scores.index)
    scores = list(np.round(similarity_scores.values, 4))

    # matches are already ordered from best to worst.
    matches = {idxs[i]: scores[i] for i in range(len(idxs))}
    return search_idx, matches
