"""
Functions to support the main Dash application in app.py

1. get_plant_details(plant_name, plant_df, image_df)
    Given a plant name, return details about the plant.

2. get_sim_opp_plant_names(selected_plant, plotting_df, axes_choice)
    Obtain the names of the three most similar and three most different plants.

3. recommend_plants(plant_df, plants_selected, cosine_sim)
    Recommend the top 6 most similar plants given 1 or multiple plants.

4. _plant_recommend_scores(plant_df, plant_name, cosine_sim)
    Determine the recommendation scores for a single plant.
"""
from typing import Tuple, Union
import numpy as np
import pandas as pd


def get_plant_details(plant_name: str, plant_df: pd.DataFrame, image_df: pd.DataFrame) -> dict:
    """
    Given a plant name, return details about the plant that can be used to
    fill out the bootstrap cards with plant info.

    Parameters
    ----------
    plant_name: str
        Plant to extract info for.

    plant_df: pd.DataFrame
        Contains basic info about each plant (e.g. sunlight, watering etc..)

    image_df : pd.DataFrame
        Contains image paths and sources for each plant.

    Returns
    ----------
    dict[str, str]
        keys are the property labels of the plant, values are the description.
    """
    filtered_image_df = image_df.iloc[image_df["Plant_Name"]
                                      .loc[lambda x: x == plant_name].index]

    filtered_plant_df = plant_df.iloc[plant_df["Plant_Name"]
                                      .loc[lambda x: x == plant_name].index]

    plant_details = {}
    plant_details["image_source"] = filtered_image_df["Website"].values[0]
    plant_details["image_path"] = filtered_image_df["File_Path"].values[0]

    common_names = filtered_plant_df["Common_Names"].values[0]
    plant_details["common_names"] = str(common_names).replace(",", ", ")

    plant_details["watering"] = filtered_plant_df["Watering"].values[0]
    plant_details["sunlight"] = filtered_plant_df["Sunlight"].values[0]
    plant_details["maintenance"] = filtered_plant_df["Maintenance"].values[0]

    plant_details["types"] = filtered_plant_df["Plant_Type"].values[0]
    plant_details["zones"] = filtered_plant_df["Zones"].values[0]
    plant_details["heights"] = filtered_plant_df["Heights"].values[0]
    plant_details["spreads"] = filtered_plant_df["Spreads"].values[0]
    plant_details["flowers"] = filtered_plant_df["Flowers"].values[0]
    plant_details["fruits"] = filtered_plant_df["Fruits"].values[0]

    return plant_details


def get_sim_opp_plant_names(selected_plant: str, plotting_df: pd.DataFrame, axes_choice: str) -> list:
    """
    Obtain the names of the three most similar and three most different plants
    according to the plant currently selected. As this works with the scatter graph
    selection, the similarity is based on the proximty of the scatter points.

    Parameters
    ----------
    plant_name: str
        Plant clicked on by user to extract info from.

    plotting_df: pd.DataFrame
        Contains axis values for the possible scatter plots that can be made.

    axes_choice: str
        What are the x and y axes currently in use by the scatter plot.

    Returns
    ----------
    list[str]
        6 Plant names, first 3 are most similar plants, last 3 are most different.
    """

    if axes_choice == "tsne_all":
        df = plotting_df[["Plant_Name", "all_tsne_1", "all_tsne_2"]]
        df.columns = ["Plant_Name", "x", "y"]

    elif axes_choice == "sunlight_water":
        df = plotting_df[["Plant_Name",
                          "Watering_jittered", "Sunlight_jittered"]]
        df.columns = ["Plant_Name", "x", "y"]

    else:
        df = plotting_df[[
            "Plant_Name", "Max_Spread_Capped_jittered", "Max_Height_Capped_jittered"]]
        df.columns = ["Plant_Name", "x", "y"]

    # determine values for the plant target.
    target_index = df.loc[df["Plant_Name"] == selected_plant].index.values[0]
    x_target = df.loc[df["Plant_Name"] == selected_plant]["x"].values[0]
    y_target = df.loc[df["Plant_Name"] == selected_plant]["y"].values[0]

    # determine magnitude of diff for each plant and find the smallest and largest.
    diffs = abs(df["x"] - x_target) + abs(df["y"] - y_target)
    # taking 4 as searched plant will be one of them...
    most_similar = diffs.nsmallest(n=4).index.values
    most_different = diffs.nlargest(n=3).index.values

    # Counting deals with possible issue that the target plant may not be one of the top 4 plants
    # (if several plants have a delta of 0).
    i = 0
    similar_names = []
    for idx in most_similar:
        if idx != target_index:
            i = + 1
            similar_names.append(df.iloc[idx]["Plant_Name"])
        if i == 3:
            break

    different_names = [df.iloc[idx]["Plant_Name"] for idx in most_different]

    return similar_names + different_names


def recommend_plants(plant_df: pd.DataFrame, plants_selected: Union[str, list], cosine_sim: np.ndarray) -> list:
    """
    Recommend the top 6 most similar plants given 1 or multiple plants.
    Similarity determined by the cosine_similarity (pre-determined).

    In the case of multiple plants to search against, each plant is weighted equally.

    Parameters
    ----------
    plant_df : pd.DataFrame
        Contains basic info about each plant (e.g. sunlight, watering etc..)

    plants_selected: Union[str, list]
        String (for single plant) or list (for multiple plants) of plant name(s) to make
        recommendations on.

    cosine_sim: np.ndarray
        Cosine similarity matrix.

    Returns
    ----------
    list[str]
        Top 6 most similar plants ordered by their scores.
    """

    # single plant to search.
    if isinstance(plants_selected, str):
        search_idx, total_scores = _plant_recommend_scores(
            plant_df=plant_df, plant_name=plants_selected, cosine_sim=cosine_sim)

        # remove the plant that was used in the search from the results
        total_scores.pop(search_idx)

    # multiple plants to search.
    else:
        search_idxs, results = [], []
        for plant in plants_selected:
            search_idx, result = _plant_recommend_scores(
                plant_df=plant_df,
                plant_name=plant,
                cosine_sim=cosine_sim)
            search_idxs.append(search_idx)
            results.append(result)

        # sum each score for each plant searched and make a combined score of
        # the same format as single search.
        total_scores = {}
        for key in results[0].keys():

            score = 0
            for idx in range(len(results)):
                score += results[idx][key]

            total_scores.update({key: round(score, 4)})

        total_scores = {k: v for k, v in sorted(
            total_scores.items(), key=lambda item: item[1], reverse=True)}

        # remove the plants that were searched for from the results
        for search_idx in search_idxs:
            total_scores.pop(search_idx)

    # convert from index and score to plant names.
    top_plants = []
    for idx, (k, v) in enumerate(total_scores.items()):
        if idx == 6:
            break
        top_plants.append(plant_df.iloc[k]["Plant_Name"])

    return top_plants


def _plant_recommend_scores(plant_df: pd.DataFrame, plant_name: str, cosine_sim: np.ndarray) -> Tuple[int, dict]:
    """
    Determine the recommendation scores for a single plant.
    All scores are returned, not only the top scores.

    Parameters
    ----------
    plant_df : pd.DataFrame
        Contains info about each plant

    plant_name: str
        Name of the plant to search for similar plants.

    cosine_sim: np.ndarray
        Cosine similarity matrix.

    Returns
    ----------
    int
        Index of the plant that is being searched.

    dict[int, float]
        Keys are the plant index and values are their score.
    """
    search_idx = plant_df.loc[plant_df["Plant_Name"] == plant_name].index[0]

    similarity_scores = pd.Series(
        cosine_sim[search_idx]).sort_values(ascending=False)
    idxs = list(similarity_scores.index)
    scores = list(np.round(similarity_scores.values, 4))

    # matches are already ordered from best to worst.
    matches = {idxs[i]: scores[i] for i in range(len(idxs))}
    return search_idx, matches
