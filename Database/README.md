## Database Overview

The SQL database (house_plants.db) was made/updated with sqlite3 and contains 7 tables.

### Tables Present:
*The Primary key is always the Latin name of the plant with the exception of the table named "cosine_sim"*.

- "latin_names": All plant Latin names available to purchase from the website blomsterlandet.se at the time of access. Produced by: "generate_database.py".

- "hyperlinks": Links for each plant to its corresponding missouribotanicalgarden.org webpage (if found/exists). Produced by: "generate_database.py", then updated by "update_database.py". Final manual additions then made with "Database_Exploration.ipynb".

- "plant_raw_data": The raw information for each plant obtained from the missouribotanicalgarden.org webpages. Produced by: get_plant_details.py

- "plant_features": Modified raw plant details into features that were then used for dimensionality reduction (for making 2D scatter plots) and for building the cosine similarity matrix. Produced by: "Step2_Feature_Engineering.ipynb".

- "plotting": X and Y coords for each plant for the possible scatter graphs a user could view in the web app. Produced by: Step3_Dimensionality_Reduction.ipynb

- "cosine_sim": The cosine similarity matrix used to make the recommendations. No primary key here as just stored as a matrix and read directly back in as a matrix. Produced by: "Step4_Recommender_System.ipynb".

- "plant_images": Paths to each image file and the website where the file was taken from.
Produced by: "get_plant_images.py" and then later updated "Resize_Images.ipynb" (so each image has the same size and width) and then finally: "Database_Exploration.ipynb" (to alter the file names after each image was compressed).
