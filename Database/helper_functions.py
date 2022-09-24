"""
Functions to help generate the various databases are stored here.
"""

import requests
from typing import Tuple
from time import sleep
from googleapiclient.discovery import build


def search_for_plant(latin_names: set, api_key: str, search_engine_id: str) -> Tuple[list, list]:
    """
    Use Googles API to search for a hyperlink about each plant on the website:
    https://www.missouribotanicalgarden.org/PlantFinder/

    Google's API key allows only 100 requests per day, so this function is called multiple times
    in order to run enough queries.

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
       Plants where a match was found. Each list item is a tuple.
       First element is plant name, second is the url.

    list
        Plants where no match was found. Each list item is a tuple.
        First element is plant name, second is the string: "no link found".
    """
    plant_with_link, plant_no_link = [], []

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


def search_save_plant_image(latin_names: list, api_key: str, search_engine_id: str) -> Tuple[list, list]:
    """
    Use Googles search API to search for an image (that is free to use or share) of each plant.

    Google's API key allows only 100 requests per day, so this function is called multiple times
    in order to run enough queries.

    Parameters
    ----------
    latin_names : list
        Plant names to google image search with.

    api_key : str
        Google api key.

    search_engine_id : str
        Google custom search id.

    Returns
    -------
    list
       Plants where an image was found. Each list item is a tuple.
       First element is plant name, second is the file path to the image and
       third is the website url where the image was taken from.

    list
        Plants where no match was found. Each list item is a tuple.
        First element is plant name, second is the string: "no image found".
    """
    request_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'}

    plant_with_image, plant_no_image = [], []

    for latin_name in latin_names:
        search_term = "\"" + latin_name + "\"" + " houseplant buy"

        resource = build("customsearch", "v1", developerKey=api_key).cse()
        result = resource.list(
            q=search_term, cx=search_engine_id, searchType="image",
            # limit search to those that are free to use or share:
            rights="(cc_publicdomain|cc_attribute|cc_sharealike|cc_noncommercial|cc_nonderived)").execute()

        try:
            image_url = result["items"][0]["link"]
            file_type = (result["items"][0]["fileFormat"]).split("/")[1]
            website_url = result["items"][0]['displayLink']

        except KeyError:  # KeyError: 'items' occurs if no search results.
            # tuple size same as plant_with_image, so easy store in SQL database
            plant_no_image.append(
                (latin_name, "no image found", "no image found"))

        else:  # if try was succesful, below executed.
            image_path = r"Database/images/" + \
                latin_name.replace(" ", "_") + "." + file_type

            img_data = requests.get(
                image_url,
                headers=request_headers).content

            with open(image_path, 'wb') as handler:
                handler.write(img_data)

            # store as tuple for ease with SQL.
            plant_with_image.append((latin_name, image_path, website_url))

        sleep(2)

    return plant_with_image, plant_no_image


if __name__ == '__main__':
    print("Why are you trying to run me?")
