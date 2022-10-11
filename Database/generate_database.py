"""
This script does the following:

1. Extract all unique Latin names for the plant avaialble to buy from blomsterlandet.se
and stored these in a database.

2. Use google's query function to run X google searches on the first Latin names
to get the webaddress for a
(googles query )
And store this in a database (both those that "worked" and those that did not).

3.
"""
import configparser
import requests
from bs4 import BeautifulSoup
import sqlite3

import helper_functions


config = configparser.ConfigParser()
config.read("Database/config.ini")
SEARCH_ENGINE_ID = config["Google Params"]["SEARCH_ENGINE_ID"]
API_KEY = config["Google Params"]["API_KEY"]
DATABASE_LOC = r"C:\Users\Rory Crean\Dropbox (lkgroup)\Backup_HardDrive\Postdoc\PyForFun\House_Plant_Recommender\Database\house_plants.db"

green_url = r"https://www.blomsterlandet.se/produkter/vaxter/inomhus/grona-vaxter/?page=50&sorting=Name&filterDefaults=false"
flowering_url = r"https://www.blomsterlandet.se/produkter/vaxter/inomhus/blommande-vaxter/?page=50&sorting=Name&filterDefaults=false"


# Which range of list items to run through the google search API.
SUBSET_START = 0
SUBSET_END = 95


def get_blomsterlandet_plants(url: str) -> list:
    """
    Using the website: https://www.blomsterlandet.se to identify all the houseplants they have available
    on a given product page. Specifically extracts the latin name assinged to each product.
    Helper function for step 1.

    Parameters
    ----------
    url : str
        Product page web address from blomsterlandet.se to scrape from.

    Returns
    -------
    set
        The scientific names of each plant.
    """
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml')

    science_section = soup.find_all(
        'p', class_="ProductCardBodystyled__ScientificName-lrzi29-3 flSCLr")

    # (first make set to remove duplicates)
    return list({science_name.get_text() for science_name in science_section})


if __name__ == '__main__':

    # 1. Generate a set of all Latin_names available to purchase from blomsterlandet.se
    green_plants = get_blomsterlandet_plants(url=green_url)
    flowering_plants = get_blomsterlandet_plants(url=flowering_url)
    plant_names = list(set(green_plants + flowering_plants))

    # reformat to that desired by the database
    plant_names_db = [(name, ) for name in plant_names]

    conn = sqlite3.connect(DATABASE_LOC)
    c = conn.cursor()

    c.execute("""DROP TABLE IF EXISTS latin_names""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS latin_names(
        Plant_Name VARCHAR (100) PRIMARY KEY
        )
    """)

    c.executemany("""INSERT INTO latin_names VALUES (?)""", plant_names_db)
    conn.commit()

    # read back out of database to ensure use same order for each follow up run.
    database_names = []
    c.execute("""SELECT * FROM 'latin_names'""")
    for row in c.fetchall():
        database_names.append(row)

    conn.close()

    # reformat for easy operations.
    latin_names = [name[0] for name in database_names]

    # 2. Run google search on the first 95 plants
    latin_names_subset = list(latin_names)[SUBSET_START:SUBSET_END]

    plant_with_link, plant_no_link = helper_functions.search_for_plant(
        latin_names=latin_names_subset, api_key=API_KEY, search_engine_id=SEARCH_ENGINE_ID)

    # 2.5 Save these to the database
    conn = sqlite3.connect(DATABASE_LOC)
    c = conn.cursor()

    c.execute("""DROP TABLE IF EXISTS hyperlinks""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS hyperlinks(
        Plant_Name VARCHAR (100) PRIMARY KEY,
        url VARCHAR (200)
        )
    """)

    c.executemany("""INSERT INTO hyperlinks VALUES (?,?)""", plant_with_link)
    c.executemany("""INSERT INTO hyperlinks VALUES (?,?)""", plant_no_link)
    conn.commit()

    c.execute("""SELECT * FROM 'hyperlinks'""")

    output = []
    found, not_found = 0, 0

    for row in c.fetchall():
        output.append(row)

        if row[1] == "no link found":
            not_found += 1
        else:
            found += 1

    print(f"Total number of links now searched: {len(output)}")
    print(f"Number of links found: {found}")
    print(f"Number of links not found: {not_found}")

    c.close()
