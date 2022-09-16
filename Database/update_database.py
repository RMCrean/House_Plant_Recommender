"""
Uses google's search API on a selected range of plant latin_names
and updates the sql database with the search results.

Google's search API only allows 100 searches per day, so this is broken up over 4 days.
There are a total of 368 names to search through so:

Day 1: Search first 95 with generate_database.py
Day 2-4: Search (up to) 95 each day using this script (argparser used to control the range on the list).
"""
import configparser
import sqlite3
import argparse

import helper_functions


config = configparser.ConfigParser()
config.read("Database/config.ini")
SEARCH_ENGINE_ID = config["Google Params"]["SEARCH_ENGINE_ID"]
API_KEY = config["Google Params"]["API_KEY"]
DATABASE_LOC = r"C:\Users\Rory Crean\Dropbox (lkgroup)\Backup_HardDrive\Postdoc\PyForFun\House_Plant_Recommender\Database\house_plants.db"

if __name__ == '__main__':

    parser_descrip = "Define the range of names from latin_names to run through the google search API."
    parser = argparse.ArgumentParser(description=parser_descrip)

    help_start = "first number to make the index the list of names, either 95 or 190 or 285"
    help_end = "second number to make the index the list of names, either 190 or 285 or 380"
    parser.add_argument("subset_start", type=int, help=help_start)
    parser.add_argument("subset_end", type=int, help=help_end)

    args = parser.parse_args()

    # Read in latin_names from database
    conn = sqlite3.connect(DATABASE_LOC)
    c = conn.cursor()

    database_names = []
    c.execute("""SELECT * FROM 'latin_names'""")
    for row in c.fetchall():
        database_names.append(row)

    # reformat and take a subset to run the calculation on.
    latin_names = [name[0] for name in database_names]
    latin_names_subset = list(latin_names)[args.subset_start:args.subset_end]

    # Run the search with the new subset.
    plant_with_link, plant_no_link = helper_functions.search_for_plant(
        latin_names=latin_names_subset, api_key=API_KEY, search_engine_id=SEARCH_ENGINE_ID)

    # 2.5 Save these into the already exisiting database
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
