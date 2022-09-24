"""
This script uses Google's image search API to obtain a picture of each houseplant
in the SQL database.

The images are saved to the folder images and their file paths and what
website they were taken from are stored inside the  SQL database for later use.

Needs to be run twice (with 24 hours gap between).
Take first 50, then take remaning 97 on the next day.

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

    help_start = "first number to make the index the list of names, either 0 or 50"
    help_end = "second number to make the index the list of names, either 50 or 150"
    help_restart = "Type: 'restart' if starting afresh, otherwise any string will do."
    parser.add_argument("subset_start", type=int, help=help_start)
    parser.add_argument("subset_end", type=int, help=help_end)
    parser.add_argument("restart", type=str, help=help_restart)

    args = parser.parse_args()

    # Read in those plant with urls available.
    conn = sqlite3.connect(DATABASE_LOC)
    c = conn.cursor()
    # <> is != in SQL.
    c.execute("""SELECT Plant_Name FROM 'hyperlinks' WHERE url<>'no link found' """)
    plants_found_list = [row for row in c.fetchall()]
    c.close()

    # Convert to list for easier handling.
    plants_found = [name[0] for name in plants_found_list]
    # filter to range to search.
    latin_names_subset = list(plants_found)[args.subset_start:args.subset_end]

    plant_with_image, plant_no_image = helper_functions.search_save_plant_image(
        latin_names=latin_names_subset,
        api_key=API_KEY,
        search_engine_id=SEARCH_ENGINE_ID
    )

    # Save these to the database
    conn = sqlite3.connect(DATABASE_LOC)
    c = conn.cursor()

    # drops table only if starting over.
    if args.restart == "restart":
        c.execute("""DROP TABLE IF EXISTS plant_images""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS plant_images(
        Plant_Name TEXT PRIMARY KEY,
        File_Path TEXT,
        Website TEXT
        )
    """)

    c.executemany("""INSERT INTO plant_images VALUES (?,?,?)""",
                  plant_with_image)
    c.executemany("""INSERT INTO plant_images VALUES (?,?,?)""",
                  plant_no_image)
    conn.commit()

    # update on current status.
    c.execute("""SELECT * FROM 'plant_images'""")
    output = []
    found, not_found = 0, 0

    for row in c.fetchall():
        output.append(row)

        if row[1] == "no image found":
            not_found += 1
        else:
            found += 1

    print(f"Total number of images now searched: {len(output)}")
    print(f"Number of images found: {found}")
    print(f"Number of images not found: {not_found}")

    c.close()
