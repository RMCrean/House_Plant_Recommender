"""
This script scrapes the missouribotanicalgarden.org webpages using the links
previously identified through the google searches (and then some follow up
manual curation).

After extracting information for each available plant the results are saved
to the SQL database for later use.
"""


import re
import requests
from typing import Tuple
from time import sleep
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3


DATABASE_LOC = r"C:\Users\Rory Crean\Dropbox (lkgroup)\Backup_HardDrive\Postdoc\PyForFun\House_Plant_Recommender\Database\house_plants.db"


def search_info_with_id(soup: BeautifulSoup, id_string: str) -> str:
    """
    Extract the text part of certain part of the HTML document using the
    unique HTML id to get the text. Only possible for some features,
    otherwise the function "search_info_without_id" is used instead.

    Parameters
    ----------
    soup : BeautifulSoup
        HTML to search through.

    id_string : str
        HTML id to search for and extract the text from.

    Returns
    -------
    str
        The text block for where the match was found.

    """
    try:
        result = soup.find("div", {"id": id_string}).contents[0].strip()
        # remove the title of the label in the text body.
        return result.split(": ")[1]
    except AttributeError:  # Catches AttributeError: 'NoneType' object has no attribute 'contents'
        # occurs if not available for this plant..
        return "None"


def search_info_without_id(soup: BeautifulSoup, string_to_match: str) -> str:
    """
    For some features to extract, the HTML id is non-specific.
    In this case, string matching is used instead.

    Parameters
    ----------
    soup : BeautifulSoup
        HTML to search through.

    string_to_match : str
        Text to match to in the text part of the HTML.

    Returns
    -------
    str
        The text block for where the match was found.
    """
    html_block = soup.find("div", class_="row")

    try:
        result = str(html_block.find(string=re.compile(string_to_match)))
        # remove the title of the label in the text body.
        return result.split(": ")[1]
    except IndexError:  # Catches IndexError: list index out of range
        # occurs if not available for this plant..
        return "None"


def extract_common_names(soup: BeautifulSoup) -> list:
    """
    Extract the common names for a given plant inside a block of html.

    If there are multiple common names, they are stored inside a widget.
    If there is only one, it is stored in "MainContentPlaceHolder_CommonNameRow".

    Parameters
    ----------
    soup : BeautifulSoup
        html to search through.

    Returns
    -------
    list
        Variable sized list (1 or more) of common names for a given plant.
    """
    html_block = str(soup.find(
        "a", {"id": "MainContentPlaceHolder_CommonNamesInfo_DisclaimerLink"}))

    re_pattern = re.compile("&lt;br/&gt;| &amp;bull; ")
    filtered_names = re.split(re_pattern, html_block)[2:]

    common_names = []
    for idx, text_block in enumerate(filtered_names):
        if "&quot" in text_block:  # after this, no more names.
            break
        if text_block != "":
            common_names.append(text_block)

    if common_names == []:  # if only one common name, then no special dialog box, so empty list
        common_names.append(search_info_with_id(
            soup=soup, id_string="MainContentPlaceHolder_CommonNameRow"))

    return common_names


def extract_all_plant_info(plant_with_link: dict) -> pd.DataFrame:
    """
    Using the web address of a given plant, extract the desired information about it from:
    missouribotanicalgarden.org.

    Parameters
    ----------
    plant_with_link : dict
        Keys are the latin names of the plants and values are web adresss to search through.

    Returns
    -------
    pd.DataFrame
        Each row is a different plant with all of the extracted features stored in different columns.
    """
    common_names, types, families = [], [], []
    zones, native_ranges = [], []
    heights, spreads = [], []
    bloom_times, bloom_descrips = [], []
    sunlights, waterings, maintenances = [], [], []
    flowers, leafs, fruits = [], [], []

    for latin_name, url in plant_with_link.items():
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'lxml')

        # special care as can be a list or str or none.
        common_names.append(extract_common_names(soup))

        types.append(search_info_with_id(
            soup=soup, id_string="MainContentPlaceHolder_TypeRow"))
        families.append(search_info_with_id(
            soup=soup, id_string="MainContentPlaceHolder_FamilyRow"))

        zones.append(search_info_with_id(
            soup=soup, id_string="MainContentPlaceHolder_ZoneRow"))
        native_ranges.append(search_info_with_id(
            soup=soup, id_string="MainContentPlaceHolder_NativeRangeRow"))

        heights.append(search_info_with_id(
            soup=soup, id_string="MainContentPlaceHolder_HeightRow"))
        spreads.append(search_info_with_id(
            soup=soup, id_string="MainContentPlaceHolder_SpreadRow"))

        bloom_times.append(search_info_with_id(
            soup=soup, id_string="MainContentPlaceHolder_BloomTimeRow"))
        bloom_descrips.append(search_info_with_id(
            soup=soup, id_string="MainContentPlaceHolder_ColorTextRow"))

        sunlights.append(search_info_with_id(
            soup=soup, id_string="MainContentPlaceHolder_SunRow"))
        waterings.append(search_info_with_id(
            soup=soup, id_string="MainContentPlaceHolder_WaterRow"))
        maintenances.append(search_info_with_id(
            soup=soup, id_string="MainContentPlaceHolder_MaintenanceRow"))

        # These 3 don't have specific ids to search through..
        flowers.append(search_info_without_id(
            soup=soup, string_to_match="Flower: "))
        leafs.append(search_info_without_id(
            soup=soup, string_to_match="Leaf: "))
        fruits.append(search_info_without_id(
            soup=soup, string_to_match="Fruit: "))

        sleep(2)  # don't want to make a load of requests at once...

    all_columns = list(zip(
        list(plant_with_link.keys()), common_names, types, families,
        zones, native_ranges,
        heights, spreads,
        bloom_times, bloom_descrips,
        sunlights, waterings, maintenances,
        flowers, leafs, fruits
    ))

    column_names = [
        "Plant_Name", "Common_Names", "Plant_Type", "Family",
        "Zones", "Native_Range",
        "Heights", "Spreads",
        "Bloom_Times", "Bloom_Description",
        "sunlight", "Watering", "Maintenance",
        "Flowers", "Leafs", "Fruits"
    ]

    return pd.DataFrame(all_columns, columns=column_names)


if __name__ == '__main__':

    # Read in those plant with urls available.
    conn = sqlite3.connect(DATABASE_LOC)
    c = conn.cursor()
    # <> is != in SQL.
    c.execute("""SELECT * FROM 'hyperlinks' WHERE url<>'no link found' """)
    plants_found_list = [row for row in c.fetchall()]
    c.close()

    # Convert to dictionary for easier handling.
    plants_found = {name[0]: name[1] for name in plants_found_list}

    # extract all the plant info
    plant_df = extract_all_plant_info(plant_with_link=plants_found)

    # convert this column from a list to a str so easy to save into SQL database.
    plant_df["Common_Names"] = [','.join(
        map(str, plant_names_list)) for plant_names_list in plant_df["Common_Names"]]

    # Now create the new database and save the generated dataframe into it.
    conn = sqlite3.connect(DATABASE_LOC)
    c = conn.cursor()

    c.execute("""DROP TABLE IF EXISTS plant_raw_data""")

    # This was used to determine comfortable values for each column.
    # for c in plant_df:
    #     if plant_df[c].dtype == 'object':
    #         print('Max length of column %s: %s\n' %  (c, plant_df[c].map(len).max()))

    c.execute("""
    CREATE TABLE IF NOT EXISTS plant_raw_data(
        Plant_Name VARCHAR (100) PRIMARY KEY,
        Common_Names VARCHAR (500),
        Plant_Type VARCHAR (80),
        Family VARCHAR (80),
        Zones VARCHAR (50),
        Native_Range VARCHAR (400),
        Heights VARCHAR (80),
        Spreads VARCHAR (80),
        Bloom_Times VARCHAR (100),
        Bloom_Description VARCHAR (200),
        sunlight VARCHAR (100),
        Watering VARCHAR (60),
        Maintenance VARCHAR (50),
        Flowers VARCHAR (100),
        Leafs VARCHAR (50),
        Fruits VARCHAR (50)
        )
    """)
    conn.commit()

    plant_df.to_sql("plant_raw_data", con=conn,
                    if_exists="append", index=False)
    # Can be read back into a df using:
    # df = pd.read_sql_query("SELECT * FROM plant_raw_data", conn)

    c.close()
