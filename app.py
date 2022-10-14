"""
Main Dash application.
To run locally simply do "python app.py" and visit: http://127.0.0.1:8050/ in your web browser.
"""
import json
import sqlite3
from typing import Tuple
import pandas as pd
import numpy as np

import plotly.graph_objects as go
import dash
from dash import html
from dash import dcc

import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import utils

################## Style Selection ##################

# https://hellodash.pythonanywhere.com/theme_explorer
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.MINTY],
    # these meta_tags ensure content is scaled correctly on different devices
    # see: https://www.w3schools.com/css/css_rwd_viewport.asp for more
    meta_tags=[{"name": "viewport",
                "content": "width=device-width, initial-scale=1"}],
    suppress_callback_exceptions=True  # https://dash.plotly.com/advanced-callbacks
)

banner_color = {"background-color": "#DEDEDE"}

content_style = {"margin-left": "2rem",
                 "margin-right": "2rem", "margin-top": "0.5rem"}

# horizontal rule styles.
hr_styles = {"v1": {"border": "2px lightgray solid"}, "v2": {
    "border": "1px lightgray solid"}, "v3": {"border": "0.5px lightgray solid"}}


################## text blocks ##################
subtitle_text = "  Because you can never have enough houseplants..."
placeholder_text = """Results for \"Plerandra elegantissima\" are currently shown,
start typing to add a plant."""

info_button_text = """Click here for an explanation of each term used in "Plant Details". """

details_explained_text = html.P([
    html.P([
        "The fact sheet for each plant was obtained from ",
        html.A("Missouri Botanical Garden, ",
               href="https://www.missouribotanicalgarden.org/", target="_blank"),
        "with the same defitions used here as found on their website."
    ]),

    html.Li([
        html.B("Maintenance: "),
        """How much work is involved in taking care of the plant.
        Options are: "High", "Medium" or "Low"."""
    ]),

    html.Li([
        html.B("Sunlight Requirements: "),
        """Recommended optimum amount of sunlight the plant should recieve.
        Options are: "Part shade to full shade", "Part shade", "Full sun to part shade", and "Full sun".
        """
    ]),

    html.Li([
        html.B("Watering Requirements: "),
        """Recommended optimum amount of watering the plant should recieve.
        Options are: "Dry", "Dry to medium", "Medium to wet" and "Wet". """
    ]),

    html.Li([html.B("Type of Plant: "), "Needs no explanation."]),

    html.Li([
        html.B("Possible Max Height Range and Possible Max Spread Range: "),
        """Max height/spread expected for a fully grown version of the plant. Note that this it is unlikely
        that the plants will be able to reach these heights if kept indoors."""
    ]),

    html.Li([
        html.B("USDA Zones: "),
        """A measure of how "cold-hardy" a plant is. The higher the number, the more cold-hardy. """,
        html.A("You can read more about this here if you're interested.",
               href="https://planthardiness.ars.usda.gov/", target="_blank"),
    ]),
    html.Li([
        html.B("Flowers and Fruits: "),
        "Does the plant produce flowers/fruits and if so what are they like?"
    ]),
])


dropdown_explain_text = html.P([
    html.P("""
    The selected plants will be used to generate the recommendations shown below.
    If you select two or more plants, the recommendations will be made based on all plants seletected,
    with each plant equally weighted).
    """),

    html.P("You can search for your plant either by it's latin name or some of its common names. "),

    html.P("You can either start typing or click the down arrow on the search box to see all available plants."),
])


sunlight_water_text_block = """Plants are seperated according to their preferance for sunlight and water.
I also "jittered" the scatter plot points (by adding a random small amount to each x and y coordinate value).
This ensures that you can see more of the points on the plot otherwise a lot would be sat on top of one another.
"""

heights_spreads_text_block = """Plants seperated by height and spread.
    The max heights and spreads were however capped to 20 feet as beyond that is probably not so
    relevant for a houseplant...
"""

tsne_all_text_block = """To seperate each plant below, 16 features were fed into a dimensioality reduction
method called t-SNE. This allowed me to convert some (not all) of the differences contained within those
16 features of each plant into just 2 dimensions, which is plotted below. The simple idea being, the closer
together two plants are on the scatter plot below, the more similar they are.
"""


##################### FAQs page #################

faq_title_1 = "What is this App?"
faq_text_1 = html.P(
    """This app recommends houseplants for you based on houseplants you already know about and like.
    You simply enter the houseplant(s) you know and like and take a look at the recommendations made and
    see if any take your fancy.""")

# TODO consider add an image here?
faq_title_2 = "How does it decide what to recommend?"
faq_text_2 = html.P([
    """This app uses a content based recommender system to identify similar plants to the ones selected by a user.
    In order to do this I pre-calculated the cosine similarity for every plant to every other plant.
    Then the plants suggested are simply those with the highest similarty score. If multiple plants are selected
    then the plants suggested have the largest sum of similarity scores to the selected plants.
    You can view the juptyer notebook I wrote to """,
    html.A("create the cosine similarity matrix here.",
           href="https://github.com/RMCrean/House_Plant_Recommender/blob/main/Step4_Recommender_System.ipynb", target="_blank"),
    html.Br(), html.Br(),
    """But that of course does not explain what was used to measure the cosine similarity for each plant combination in the first place.
    For this I took the information shown in the "Plant Details" section and used these as features to describe the plants.
    As can be seen in the "Plant Details" sections, many of these items are categorical but were converted to numerical values through
    a mix of ordinal and one-hot encoding. In the end, 16 features were created to calculate the cosine similarities scores,
    with each feature normalised so as to prevent one (or a few) features dominating the calculation.
    You can view the juptyer notebook I wrote to """,
    html.A("create the features here.",
           href="https://github.com/RMCrean/House_Plant_Recommender/blob/main/Step2_Feature_Engineering.ipynb", target="_blank"),
],)


faq_title_3 = "I can't find my plant?"
faq_text_3 = html.P("""As you can imagine there are a lot of houseplants out there, and
    this database consists of only 147 plants, so many are missing. With more time and effort
    more plants could be added, but this is supposed to be a fun side project...""")


faq_title_4 = "How did you obtain this data?"
faq_text_4 = html.P([

    html.B("The following websites/APIs were used in order to obtain the required data to make this webpage:"),
    html.Br(), html.Br(),

    html.Li([
        html.A("Blomsterlandet: ",
               href="https://www.blomsterlandet.se", target="_blank"),
        """
         The house plants available to purchase from Blomsterlandet were obtained via
        web-scraping. In this case I extracted the latin name of each houseplant possible
        to purchase.
        """,
        html.A("You can see the script I used to do this by clicking here.",
               href="https://github.com/RMCrean/House_Plant_Recommender/blob/main/Database/generate_database.py", target="_blank"),
    ]),

    html.Br(),
    html.Li([
        html.A("Missouri Botanical Garden: ",
               href="https://www.missouribotanicalgarden.org/", target="_blank"),
        "This website contains a database of information for many plants, and a ",
        html.A("script was written ",
            href="https://github.com/RMCrean/House_Plant_Recommender/blob/main/Database/get_plant_details.py",
            target="_blank"),
        "to extract and store the information stored for each houseplant.",
    ]),

    html.Br(),
    html.Li([
        html.A("Google's Custom Search API: ",
               href="https://developers.google.com/custom-search/v1/overview", target="_blank"),

        """The search API was used towards two things:
        (1) To make automated google image searches for each plant in the database, you can """,
        html.A("click here to see the script I used to search for images.",
               href="https://github.com/RMCrean/House_Plant_Recommender/blob/main/Database/get_plant_images.py",
               target="_blank"),
        """(2) To search for each plant's web address in the Missouri Botanical Garden database.
        As google's search API limits free users to 100 searches per day max and I had 368 plant names
        to search through. I wrote a """,
        html.A("script to search the first block of plants ",
               href="https://github.com/RMCrean/House_Plant_Recommender/blob/main/Database/generate_database.py",
               target="_blank"),
        """, and then wrote a """,
        html.A("second script to search through the remaining plants over the course of 3 days.",
               href="https://github.com/RMCrean/House_Plant_Recommender/blob/main/Database/update_database.py",
               target="_blank"),
    ]),

])

faq_title_5 = "I Have a Comment/Suggestion/Issue"

faq_text_5 = html.P([
    "All comments, suggestions, issues etc... are very welcome on the app's ",
    html.A("Github repository",
           href="https://github.com/RMCrean/House_Plant_Recommender", target="_blank"),
    ". You can also contact me via ",
    html.A("LinkedIn", href="https://www.linkedin.com/in/rory-crean/",
           target="_blank"),
    " if you prefer. Thank you for taking a look at my web app."
])


################## load in data ##################
DATABASE_LOC = r"Database\house_plants.db"

# setup connection
conn = sqlite3.connect(DATABASE_LOC)
c = conn.cursor()


# main df of info.
plant_df = pd.read_sql_query("SELECT * FROM plant_raw_data", conn)

# For the scatter plots
plotting_df = pd.read_sql_query("SELECT * FROM plotting", conn)

# plant images paths.
image_df = pd.read_sql_query("SELECT * FROM plant_images", conn)

# cosine_similarity matrix.
c.execute("SELECT * FROM cosine_sim")
raw_cosine_sim = c.fetchall()
cosine_sim = np.asarray(json.loads(raw_cosine_sim[0][1]))

# Finally...
c.close()


################## data preprocessing ##################

# for the search dropdown callback.
# Allows a user to search both the latin and common names.
common_names = list(plant_df["Common_Names"])
common_names_fixed = [names.replace(",", ", ") for names in common_names]

# taking only first 5 common names as otherwise too many and lines overlap...
common_names_show = []
for names in common_names_fixed:
    first_few_names = names.split(",")[0:3]
    common_names_show.append(",".join(first_few_names))

# Create a dict of latin names and selected common_names.
intermed_dict = {}
for latin_name, common_names in zip(list(plant_df["Plant_Name"]), common_names_show):
    intermed_dict.update({latin_name: common_names})

#  dict in alphabetical order.
sorted_dict = {key: value for key, value in sorted(intermed_dict.items())}
sorted_dict

# format for dash
plant_search_options = []
for latin_name, plant_common_names in sorted_dict.items():
    plant_search_options.append(
        {"label": str(latin_name + ", Commonly known as: " + plant_common_names),
         "value": latin_name}
    )


################## App layout ##################

# Banner part of page - same for all webpages.
page_banner = [

    dbc.Row([
        dbc.Col([
            html.H2("Houseplant Recommender",
                    className="display-4 text-success"),
        ], xs=8, sm=8, md=6, lg=4, xl=4),

        dbc.Col([
            dbc.Nav(
                [
                    dbc.NavLink("Generate Recommendations", href="/", active="exact",
                                style={"font-size": "22px"}),
                    dbc.NavLink("Visualise How all Plants Compare",
                                href="/comparisons", active="exact", style={"font-size": "22px"}),
                    dbc.NavLink("FAQs", href="/FAQs", active="exact",
                                style={"font-size": "22px"}),
                ],
                pills=True,
            ),
        ], xs=8, sm=8, md=8, lg=8, xl=8),
    ], style=banner_color),


    dbc.Row([
        html.P(subtitle_text, className="lead text-success"),
        html.Hr(style=hr_styles["v2"]),
        html.Br(), html.Br(),
    ], style=banner_color),
]


# blank content with central layout defined by the callbacks.
content = html.Div(id="page-content", children=[], style=content_style)

app.layout = dbc.Container([
    dcc.Location(id="url"),
    content
], fluid=True)


# Landing page with recommendations made.
recommend_page = [
    page_banner[0],
    page_banner[1],
    html.Br(),

    # Row2 - enter plant name.
    dbc.Row([
        dbc.Col([
            html.H3("Select the plant(s) that you want to generate your recommendations from",
                className="text-center text-success mb-2"),
            html.Br(),
            dropdown_explain_text,
            dcc.Dropdown(
                id="dropdown-plant-select", multi=True, clearable=True,
                options=plant_search_options, placeholder=placeholder_text,
                value="Plerandra elegantissima",
            ),
        ], xs=12, sm=12, md=8, lg=8, xl=6,  style={"justify-content": "left"}, className="mb-2"),

        dbc.Col(dbc.Card([], id="plant_card_p1",
                         color="primary", outline=True),
                xs=12, sm=12, md=8, lg=6, xl=3, className="mb-2"),

        dbc.Col(dbc.Card([], id="plant_card_p2",
                         color="primary", outline=True),
                xs=12, sm=12, md=8, lg=6, xl=3, className="mb-2"),

    ], justify="center"),

    # Row.
    dbc.Row([
        html.Br(), html.Br(),
        dbc.Button(info_button_text, color="info",
                   id="recommend-help-button", block=True),
        dbc.Modal(
            [
                dbc.ModalHeader("What does each Label Mean?"),
                dbc.ModalBody(details_explained_text),
                dbc.ModalFooter(
                    dbc.Button(
                        "Close", id="close", className="ms-auto", n_clicks=0
                    )
                ),
            ],
            id="modal",
            is_open=False,
        ),
    ], justify="center"),

    # Row4
    dbc.Row([
        html.Hr(style=hr_styles["v2"]),
    ]),

    # Row4 - Subtitle for recommendations
    dbc.Row([
        dbc.Col([
            html.H3("The Top 6 Recommendations Based on your Selected Plant(s)",
                    className="text-center text-success mb-4"),

        ], width=12),
    ], justify="center"),

    # Row6 - recommendations, 1st row.
    dbc.Row([
        dbc.Col(dbc.Card([], id="recommend_card_1",
                         color="primary", outline=True),
                xs=12, sm=12, md=6, lg=4, xl=4, className="mb-2"),
        dbc.Col(dbc.Card([], id="recommend_card_2",
                         color="primary", outline=True),
                xs=12, sm=12, md=6, lg=4, xl=4, className="mb-2"),
        dbc.Col(dbc.Card([], id="recommend_card_3",
                         color="primary", outline=True),
                xs=12, sm=12, md=6, lg=4, xl=4, className="mb-2"),
    ], justify="center"),

    # Row7 - recommendations, 2nd row.
    dbc.Row([
        dbc.Col(dbc.Card([], id="recommend_card_4",
                         color="primary", outline=True),
                xs=12, sm=12, md=6, lg=4, xl=4, className="mb-2"),
        dbc.Col(dbc.Card([], id="recommend_card_5",
                         color="primary", outline=True),
                xs=12, sm=12, md=6, lg=4, xl=4, className="mb-2"),
        dbc.Col(dbc.Card([], id="recommend_card_6",
                         color="primary", outline=True),
                xs=12, sm=12, md=6, lg=4, xl=4, className="mb-2"),
    ], justify="center"),

]

# Compare each plant on a scatter plot.
comparisons_page = [
    page_banner[0],
    page_banner[1],
    html.Br(),

    # New row - dialog buttons to control the scatter plot.
    dbc.Row([
        dbc.Col([
            html.H3("See how all the different houseplants compare",
                    className="text-center text-success mb-2"),
            # TODO Add explanation on how taken above features to use scatter plot.

        ], className="mb-2"),
    ], justify="center"),

    # Row3 -
    dbc.Row([

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5(
                        ["Control the graph axes with the radio buttons."], className="text-center"),
                    dbc.RadioItems(
                        options=[
                            {"label": "Sunlight and watering Requirements",
                             "value": "sunlight_water"},
                            {"label": "Possible Plant Heights and Spreads",
                             "value": "heights_spreads"},
                            {"label": "Seperate by everything!",
                             "value": "tsne_all", },
                        ],
                        value="sunlight_water", id="graph_radio_buttons", inline=True,
                        className="text-center"
                    ),
                    html.P(id="scatter-info-block", children=[]),
                    dcc.Graph(id="scatter-graph", figure={}),
                ]),
            ]),
        ], xs=12, sm=12, md=12, lg=8, xl=8, className="mb-2"),

        dbc.Col([
            dbc.Card(id="scatter-info-card",
                children=[
                    dbc.CardBody([
                        html.H5("Click on any houseplant on the scatter graph and this box will become populated!",
                                className="card-title text-center"),
                        html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(
                        ), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),
                        html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(
                        ), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),
                    ]),
                ]
            ),
        ], xs=12, sm=12, md=12, lg=4, xl=4, className="mb-2"),

    ], justify="center"),

    # Row6 - 3 most similar
    dbc.Row([
        dbc.Col(dbc.Card([], id="most_sim_card_1",
                         color="primary", outline=True),
                xs=12, sm=12, md=6, lg=4, xl=4, className="mb-2"),
        dbc.Col(dbc.Card([], id="most_sim_card_2",
                         color="primary", outline=True),
                xs=12, sm=12, md=6, lg=4, xl=4, className="mb-2"),
        dbc.Col(dbc.Card([], id="most_sim_card_3",
                         color="primary", outline=True),
                xs=12, sm=12, md=6, lg=4, xl=4, className="mb-2"),
    ], justify="center"),

    # Row7 - 3 most diff.
    dbc.Row([
        dbc.Col(dbc.Card([], id="most_diff_card_1",
                         color="secondary", outline=True),
                xs=12, sm=12, md=6, lg=4, xl=4, className="mb-2"),
        dbc.Col(dbc.Card([], id="most_diff_card_2",
                         color="secondary", outline=True),
                xs=12, sm=12, md=6, lg=4, xl=4, className="mb-2"),
        dbc.Col(dbc.Card([], id="most_diff_card_3",
                         color="secondary", outline=True),
                xs=12, sm=12, md=6, lg=4, xl=4, className="mb-2"),
    ], justify="center"),


]


# FAQs page...
faqs_page = [
    page_banner[0],
    page_banner[1],
    html.Br(),
    html.H3("Frequently asked questions (FAQs)",
            className="text-center text-success mb-2"),
    html.Br(),
    dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5(faq_title_1),
                    html.Hr(style=hr_styles["v3"]),
                    html.P(faq_text_1),
                ]),
            ], color="primary", outline=True),
            ], width=12, className="mb-2"),
    dbc.Col([
        dbc.Card([
            dbc.CardBody([
                html.H5(faq_title_2),
                html.Hr(style=hr_styles["v3"]),
                html.P(faq_text_2),
            ]),
        ], color="primary", outline=True),
    ], width=12, className="mb-2"),
    dbc.Col([
        dbc.Card([
            dbc.CardBody([
                html.H5(faq_title_3),
                html.Hr(style=hr_styles["v3"]),
                html.P(faq_text_3),
            ]),
        ], color="primary", outline=True),
    ], width=12, className="mb-2"),
    dbc.Col([
        dbc.Card([
            dbc.CardBody([
                html.H5(faq_title_4),
                html.Hr(style=hr_styles["v3"]),
                html.P(faq_text_4),
            ]),
        ], color="primary", outline=True),
    ], width=12, className="mb-2"),
    dbc.Col([
        dbc.Card([
            dbc.CardBody([
                html.H5(faq_title_5),
                html.Hr(style=hr_styles["v3"]),
                html.P(faq_text_5),
            ]),
        ], color="primary", outline=True),
    ], width=12, className="mb-2"),
]


##################  Callbacks ##################


# Page navigation.
@ app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def define_location(pathname):
    """Callback to move user to the correct page."""
    if pathname == "/":
        return recommend_page

    elif pathname == "/comparisons":
        return comparisons_page

    elif pathname == "/FAQs":
        return faqs_page

    # If the user tries to reach a different page, return a 404 message
    else:
        return dbc.Jumbotron([
            html.H1("404: Not found", className="text-danger"),
            html.Hr(style=hr_styles["v1"]),
            html.P(f"The pathname {pathname} was not recognised..."),
        ])


# upgrade dropdown.
@ app.callback(
    dash.dependencies.Output("dropdown-plant-select", "options"),
    [dash.dependencies.Input("dropdown-plant-select", "search_value")],
    [dash.dependencies.State("dropdown-plant-select", "value")],
)
def dynamic_dropdown_options(search_value, value):
    """
    Callback for "dropdown-plant-select" with case insensitive search enabled.

    """
    if not search_value:
        raise PreventUpdate
    # Make sure that the set values are in the option list, else they will disappear
    # from the shown select list, but still part of the `value`.
    return [o for o in plant_search_options if search_value.upper() in o["label"].upper() or o["value"] in (value or [])]


# help popup modal - modulate open vs closed status.
@app.callback(
    Output("modal", "is_open"),
    [Input("recommend-help-button", "n_clicks"), Input("close", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


# Info card for last selected plant.
@ app.callback(
    [Output("plant_card_p1", "children"),
     Output("plant_card_p2", "children")],
    Input("dropdown-plant-select", "value"),
)
def make_plant_card(plant_selection: Tuple[str, list]):
    """
    Makes the plant card that shows the user what plant they have selected.

    """
    # only show the last selected plant.
    if isinstance(plant_selection, str):
        plant_name = plant_selection
    else:
        plant_name = str(plant_selection[-1])

    plant_details = utils.get_plant_details(
        plant_name=plant_name, plant_df=plant_df, image_df=image_df)

    card_content_p1 = [
        dbc.Button(f"Last Selected Plant: {plant_name}",
                   color="success", className="me-1"),
        html.Br(),
        dbc.CardImg(src=plant_details['image_path']),

        dbc.CardBody([
            html.P(f"Image obtained from: {plant_details['image_source']}",
                   className="card-text text-right font-italic"),
            html.P(
                f"Commonly known as: {plant_details['common_names']}",
                className="card-text"),
        ]),
    ]

    card_content_p2 = [
        dbc.Button("Plant Details", color="info", className="me-1"),
        dbc.CardBody(
            [
                dbc.ListGroup([
                    dbc.ListGroupItem(
                        f"Maintenance: {plant_details['maintenance']}"),
                    dbc.ListGroupItem(
                        f"Sunlight Requirements: {plant_details['sunlight']}"),
                    dbc.ListGroupItem(
                        f"Watering Requirements: {plant_details['watering']}"),
                    dbc.ListGroupItem(
                        f"Type of Plant: {plant_details['types']}"),
                    dbc.ListGroupItem(
                        f"Possible Max Height Range: {plant_details['heights']}"),
                    dbc.ListGroupItem(
                        f"Possible Max Spread Range: {plant_details['spreads']}"),
                    dbc.ListGroupItem(f"USDA Zones: {plant_details['zones']}"),
                    dbc.ListGroupItem(
                        f"Flowers: {plant_details['flowers']}"),
                    dbc.ListGroupItem(
                        f"Fruits: {plant_details['fruits']}"),
                ], className="card-text", flush=True),
            ]
        ),
    ]

    return card_content_p1, card_content_p2


# Update each of the recommendation cards...
@app.callback(
    [
        Output("recommend_card_1", "children"),
        Output("recommend_card_2", "children"),
        Output("recommend_card_3", "children"),
        Output("recommend_card_4", "children"),
        Output("recommend_card_5", "children"),
        Output("recommend_card_6", "children"),

    ],
    Input("dropdown-plant-select", "value"),
)
def give_recommendations(plant_selection):
    """
    Uses the cosine similarity matrix and user selected plants to
    find top 6 plants to recommend.
    """
    top_plants = utils.recommend_plants(
        plant_df=plant_df,
        plants_selected=plant_selection,
        cosine_sim=cosine_sim)

    all_plant_details = []
    for plant_name in top_plants:
        all_plant_details.append(
            utils.get_plant_details(
                plant_name=plant_name,
                plant_df=plant_df,
                image_df=image_df
            )
        )

    all_card_content = []
    for idx, plant_details in enumerate(all_plant_details):
        card_content = [
            dbc.Card([
                dbc.Button(
                    f"Number {(idx + 1)}: {top_plants[idx]}", color="success", className="card-title text-center"),
                dbc.CardImg(src=plant_details['image_path']),

                dbc.CardBody([
                    html.P(f"Image obtained from: {plant_details['image_source']}",
                           className="card-text text-right font-italic"),
                    html.P(
                        f"Commonly known as: {plant_details['common_names']}",
                        className="card-text"),
                ]),
            ], style={"border": "none", "outline": "none"},),

            dbc.CardBody([
                dbc.ListGroup([
                    dbc.Button("Plant Details",
                               color="info",
                               className="card-title text-center",
                               ),
                    dbc.ListGroupItem(
                        f"Maintenance: {plant_details['maintenance']}"),
                    dbc.ListGroupItem(
                        f"Sunlight Requirements: {plant_details['sunlight']}"),
                    dbc.ListGroupItem(
                        f"Watering Requirements: {plant_details['watering']}"),
                    dbc.ListGroupItem(
                        f"Type of Plant: {plant_details['types']}"),
                    dbc.ListGroupItem(
                        f"Possible Max Height Range: {plant_details['heights']}"),
                    dbc.ListGroupItem(
                        f"Possible Max Spread Range: {plant_details['spreads']}"),
                    dbc.ListGroupItem(f"USDA Zones: {plant_details['zones']}"),
                    dbc.ListGroupItem(
                        f"Flowers: {plant_details['flowers']}"),
                    dbc.ListGroupItem(
                        f"Fruits: {plant_details['fruits']}"),
                ], className="card-text", flush=True),
            ]),
        ]

        all_card_content.append(card_content)

    return all_card_content


# Update scatter graph callback
@ app.callback(
    [Output("scatter-graph", "figure"),
     Output("scatter-info-block", "children"),
     ],
    Input("graph_radio_buttons", "value"),
)
def gen_scatter_plot(axes_choice):
    """
    Choose the axes to show for the scatter plot based on user input.
    # TODO - split based on what can be generic....
    # TODO - text states, name + non-unique names perhaps?
    """
    if axes_choice == "tsne_all":
        x = plotting_df["all_tsne_1"]
        y = plotting_df["all_tsne_2"]
        axis_titles = ["tSNE 1", "tSNE 2"]
        annotations = []
        axis_params = {"x": dict(showticklabels=True),
                       "y": dict(showticklabels=True)}

        info_block = tsne_all_text_block

    elif axes_choice == "sunlight_water":
        x = plotting_df["Watering_jittered"]
        y = plotting_df["Sunlight_jittered"]
        axis_titles = ["", ""]
        axis_params = {"x": dict(showticklabels=False),
                       "y": dict(showticklabels=False)}
        annotations = [
            dict(
                text="Requires More Watering", align="center",
                ax=3, x=3, xref="x", axref="x",
                ay=-0.18, y=-0.18, yref="paper",
                showarrow=False,
            ),
            dict(
                ax=0.6, x=5.4, xref="x", axref="x",
                ay=-0.05, y=-0.05, yref="paper",
                showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=3,
                arrowcolor="#645754",
            ),
            dict(
                text="Requires More Sunlight", align="center", textangle=-90,
                ax=-0.1, x=-0.1, xref="paper", axref="x",
                ay=2.5, y=2.5, yref="y", ayref="y",
                showarrow=False
            ),
            dict(
                ax=-0.06, x=-0.06, xref="paper",
                ay=0, y=4.8, yref="y", ayref="y",
                showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=3,
                arrowcolor="#645754",
            ), ]

        info_block = sunlight_water_text_block

    else:
        x = plotting_df["Max_Spread_Capped_jittered"]
        y = plotting_df["Max_Height_Capped_jittered"]
        axis_titles = ["Max Spread (feet)", "Max Height (feet)"]
        annotations = []
        axis_params = {"x": dict(showticklabels=True),
                       "y": dict(showticklabels=True)}

        info_block = heights_spreads_text_block

    # Now make the figure object.
    fig = go.Figure(data=go.Scatter(
        x=x, y=y, mode="markers",
        text=plotting_df["Plant_Name"],
        marker=dict(
            size=10,
            color=plotting_df["Maintenance_Ordinal"],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(
                title="Maintenance Level", ticks="outside", tickmode="array", orientation="h",
                tickvals=[1, 2, 3], dtick=1, ticktext=["Low", "Moderate", "High"])
        )
    ))

    fig.update_traces(
        hovertemplate="<b>%{text} </b><extra></extra>",
    )

    fig.update_layout(
        xaxis_title=axis_titles[0], yaxis_title=axis_titles[1],
        plot_bgcolor="rgb(223,235,245)",
        annotations=annotations,
        xaxis=axis_params["x"],
        yaxis=axis_params["y"],
    )

    # weird behaviour with this axes not being placed correctly automatically.
    if axes_choice == "tsne_all":
        fig.update_xaxes(
            tickangle=90,
            title_text="tSNE 1",
            title_standoff=25)

    return fig, info_block


# Update Info card generated for the scatter graph Main info cards.
@ app.callback(
    [Output("scatter-info-card", "children"),
     Output("most_sim_card_1", "children"),
     Output("most_sim_card_2", "children"),
     Output("most_sim_card_3", "children"),
     Output("most_diff_card_1", "children"),
     Output("most_diff_card_2", "children"),
     Output("most_diff_card_3", "children")],
    [Input("scatter-graph", "clickData"),
     Input("graph_radio_buttons", "value")],
    prevent_initial_call=True  # because I am reliant on a user click.
)
def make_scatter_cards(clickData, axes_choice):
    """Card generated when click scatter graph"""
    if clickData is not None:
        plant_name = clickData["points"][0]["text"]

        plant_details = utils.get_plant_details(
            plant_name=plant_name, plant_df=plant_df, image_df=image_df)

        # First build card for plant clicked on.
        card_content_clicked = [
            dbc.Card([
                dbc.Button(
                    f"Selected Plant: {plant_name}", color="success", className="card-title text-center"),
                dbc.CardImg(src=plant_details['image_path']),
                dbc.CardBody([
                    html.P(f"Image obtained from: {plant_details['image_source']}",
                           className="card-text text-right font-italic"),
                    html.P(
                        f"Commonly known as: {plant_details['common_names']}",
                        className="card-text"),
                ]),
            ], style={"border": "none", "outline": "none"},),

            dbc.CardBody([
                dbc.ListGroup([
                    dbc.Button("Plant Details",
                               color="info",
                               className="card-title text-center",
                               ),
                    dbc.ListGroupItem(
                        f"Maintenance: {plant_details['maintenance']}"),
                    dbc.ListGroupItem(
                        f"Sunlight Requirements: {plant_details['sunlight']}"),
                    dbc.ListGroupItem(
                        f"Watering Requirements: {plant_details['watering']}"),
                    dbc.ListGroupItem(
                        f"Type of Plant: {plant_details['types']}"),
                    dbc.ListGroupItem(
                        f"Possible Max Height Range: {plant_details['heights']}"),
                    dbc.ListGroupItem(
                        f"Possible Max Spread Range: {plant_details['spreads']}"),
                    dbc.ListGroupItem(f"USDA Zones: {plant_details['zones']}"),
                    dbc.ListGroupItem(
                        f"Flowers: {plant_details['flowers']}"),
                    dbc.ListGroupItem(
                        f"Fruits: {plant_details['fruits']}"),
                ], className="card-text", flush=True),
            ]),
        ]

        # Now build cards for suggested plants.
        # 1st 3 are most similar, next 3 are most different.
        sim_diff_names = utils.get_sim_opp_plant_names(
            selected_plant=plant_name,
            plotting_df=plotting_df,
            axes_choice=axes_choice)

        sim_diff_plant_details = []
        for plant_name in sim_diff_names:
            sim_diff_plant_details.append(utils.get_plant_details(
                plant_name=plant_name, plant_df=plant_df, image_df=image_df)
            )

        sim_diff_card_content = []
        for idx, plant_details in enumerate(sim_diff_plant_details):

            if idx > 2:
                rank = idx - 3
                button_color = "secondary"
            else:
                rank = idx
                button_color = "primary"

            card_content = [
                dbc.Card([
                    dbc.Button(
                        f"Number {(rank + 1)}: {sim_diff_names[idx]}", color=button_color, className="card-title text-center"),
                    dbc.CardImg(src=plant_details['image_path']),

                    dbc.CardBody([
                        html.P(f"Image obtained from: {plant_details['image_source']}",
                               className="card-text text-right font-italic"),
                        html.P(
                            f"Commonly known as: {plant_details['common_names']}",
                            className="card-text"),
                    ]),
                ], style={"border": "none", "outline": "none"},),

                dbc.CardBody([
                    dbc.ListGroup([
                        dbc.Button("Plant Details",
                                   color="info",
                                   className="card-title text-center",
                                   ),
                        dbc.ListGroupItem(
                            f"Maintenance: {plant_details['maintenance']}"),
                        dbc.ListGroupItem(
                            f"Sunlight Requirements: {plant_details['sunlight']}"),
                        dbc.ListGroupItem(
                            f"Watering Requirements: {plant_details['watering']}"),
                        dbc.ListGroupItem(
                            f"Type of Plant: {plant_details['types']}"),
                        dbc.ListGroupItem(
                            f"Possible Max Height Range: {plant_details['heights']}"),
                        dbc.ListGroupItem(
                            f"Possible Max Spread Range: {plant_details['spreads']}"),
                        dbc.ListGroupItem(
                            f"USDA Zones: {plant_details['zones']}"),
                        dbc.ListGroupItem(
                            f"Flowers: {plant_details['flowers']}"),
                        dbc.ListGroupItem(
                            f"Fruits: {plant_details['fruits']}"),
                    ], className="card-text", flush=True),
                ]),
            ]

            sim_diff_card_content.append(card_content)
        print(len(sim_diff_card_content))

    return card_content_clicked, sim_diff_card_content[0], sim_diff_card_content[1], sim_diff_card_content[2], sim_diff_card_content[3], sim_diff_card_content[4], sim_diff_card_content[5],


################## End of app ##################
if __name__ == "__main__":
    app.run_server(debug=True)  # TODO - remove when ready.
