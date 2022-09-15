"""
Functions to help generate the various databases are stored here.
"""

import re
import requests
from typing import Tuple
from time import sleep
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
import pandas as pd


def search_for_plant(latin_names: set, api_key: str, search_engine_id: str) -> Tuple[list, list]:
    """
    Use Googles API to search for a hyperlink about each plant on the website:
    https://www.missouribotanicalgarden.org/PlantFinder/

    Google's API key allows only 100 requests per day, so this function is called multiple times
    in order to run enough queries (269 in total needed).

    Parameters
    ----------
    latin_names : set
        set of the plant latin_names to google search with.

    api_key : str
        Google api key.

    search_engine_id : str
        Google custom search id.

    Returns
    -------
    list
        All scientific names of each plant, stored as set to avoid duplication.

    """
    plant_no_link = []
    plant_with_link = []

    for latin_name in latin_names:
        search_term = "\"" + latin_name + "\"" + \
            " site:http://www.missouribotanicalgarden.org"

        resource = build("customsearch", 'v1', developerKey=api_key).cse()
        result = resource.list(q=search_term, cx=search_engine_id).execute()

        match_me = "https://www.missouribotanicalgarden.org/PlantFinder/PlantFinderDetails"

        try:
            top_result = result["items"][0]["link"]
            if top_result != None and match_me in top_result:
                plant_with_link.append((latin_name, top_result))
            else:
                plant_no_link.append((latin_name, "no link found"))

        except KeyError:  # KeyError: 'items' occurs if no search results.
            plant_no_link.append((latin_name, "no link found"))

        sleep(2)
    return plant_with_link, plant_no_link


if __name__ == '__main__':
    print("Why are you trying to run me?")
