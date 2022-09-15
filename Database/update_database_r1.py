"""
Runs a google search through list items 95-190 (of plant latin names)
and store the results inside the database.
"""
import configparser
import sqlite3

import helper_functions


config = configparser.ConfigParser()
config.read("Database/config.ini")
SEARCH_ENGINE_ID = config["Google Params"]["SEARCH_ENGINE_ID"]
API_KEY = config["Google Params"]["API_KEY"]
DATABASE_LOC = r"C:\Users\Rory Crean\Dropbox (lkgroup)\Backup_HardDrive\Postdoc\PyForFun\House_Plant_Recommender\Database\house_plants.db"

# Which range of list items to run through the google search API.
SUBSET_START = 95
SUBSET_END = 190


if __name__ == '__main__':

    # Read in latin_names from database
    conn = sqlite3.connect(DATABASE_LOC)
    c = conn.cursor()

    database_names = []
    c.execute("""SELECT * FROM 'latin_names'""")
    for row in c.fetchall():
        database_names.append(row)

    # reformat and take a subset to run the calculation on.
    latin_names = [name[0] for name in database_names]
    latin_names_subset = list(latin_names)[SUBSET_START:SUBSET_END]

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
