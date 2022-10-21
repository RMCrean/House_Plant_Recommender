# Houseplant Recommender

A recommender engine to suggest house plants for you. The recommender engine is presented as part of a dashboard/app hosted on Python Anywhere: https://houseplantrecommender.pythonanywhere.com/ Please feel free to check it out!


### How does the recommender engine work?
This app uses a content based recommender system to identify similar plants to the ones selected. In order to do this I pre-calculated the cosine similarity for every plant to every other plant. Then the plants suggested are simply those with the highest similarity score. If multiple plants are selected then the plants suggested have the largest sum of similarity scores to the selected plants. [The Jupyter notebook I wrote to create the cosine similarity matrix is included in this repo.](https://github.com/RMCrean/House_Plant_Recommender/blob/main/Step4_Recommender_System.ipynb)

But that of course does not explain what was used to measure the cosine similarity for each plant combination in the first place. For this I took the information shown in the "Plant Details" section of the dashboard/app and used these as features to describe the plants. As can be seen in the "Plant Details" sections, many of these items are categorical but were converted to numerical values primarily through a mix of ordinal and one-hot encoding. In the end, 16 features were created to calculate the cosine similarities scores, with each feature normalized so as to prevent one (or a few) features dominating the calculation. You can view the Jupyter notebook I wrote to create the features here.


### How did you obtain this data?
*The data required for this project is stored in a sqlite3 database (see the Database subfolder). Included is a README file describing how the contents of the database.*

**The following websites/APIs were used in order to obtain the required data to make this webpage:**

1. [Blomsterlandet](https://www.blomsterlandet.se/): The house plants available to purchase from Blomsterlandet were obtained via web-scraping. In this case I extracted the Latin name of each houseplant that was available to be purchased. You can see the script I used to do this by [clicking here](https://github.com/RMCrean/House_Plant_Recommender/blob/main/Database/generate_database.py).

2. [Missouri Botanical Garden](https://www.missouribotanicalgarden.org/): This website contains a database of information for many plants, and a script was written to extract and store the information stored for each houseplant.

3. [Google's Custom Search API](https://developers.google.com/custom-search/v1/overview): The search API was used towards two things: (1) To make automated google image searches for each plant in the database. You can [click here to see the script](https://github.com/RMCrean/House_Plant_Recommender/blob/main/Database/get_plant_images.py) I used to do this. (2) To search for each plant's web address in the Missouri Botanical Garden database. As Google's search API limits free users to 100 searches per day, and I had 368 plant names to search through. I [wrote a script to search the first block of plants](https://github.com/RMCrean/House_Plant_Recommender/blob/main/Database/generate_database.py), and then wrote [a second script to search through the remaining plants](https://github.com/RMCrean/House_Plant_Recommender/blob/main/Database/update_database.py) over the course of 3 days.


### How could I run this app locally?
To run this app you will need to install Dash which includes the plotly graphing library. [Click here for instructions on how to do this.](https://dash.plotly.com/installation)

**To run the app you would then need to have downloaded at least the following files:**
- app.py
- utils.py
- Database\house_plants.db
- All images inside the folder: assets

Then, keeping the directory structure the same you can simply type: "python app.py"
and visit "http://127.0.0.1:8050/" on a web browser.

### I have a comment/suggestion/issue
All comments, suggestions, issues etc... are very welcome, feel free to open an issue/pull request. You can also contact me via [LinkedIn](https://www.linkedin.com/in/rory-crean/) if you prefer. Thanks for taking a look at this repo and the web app!