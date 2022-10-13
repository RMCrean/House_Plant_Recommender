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

info_button_text = "Click here for an explanation of each term used"

dropdown_explain_text = html.P([
    html.P("""
    The selected plants will be used to generate the recommendations shown below.
    If you select two or more plants, the recommendations will be made based on all plants seletected,
    with each plant will be equally weighted).
    """),

    html.P("You can search for your plant either by it's latin name or some of its common names. "),

    html.P("You can either start typing or click the down arrow on the search box to see all available plants."),
])


faq_title_1 = "What is this App?"
faq_text_1 = html.P(
    """This app lets you """
)

faq_title_2 = "How does it decide what to recommend?"
faq_text_2 = html.P(
    """This app lets you """
)


faq_title_3 = "I can't find my plant?"
faq_text_3 = html.P(
    """
As you can imagine there are a lot of houseplants out there, and this database
is made up of 147 plants, so many are missing.
This depends on many things....

"""
)


faq_title_4 = "How did you obtain this data?"
faq_text_4 = html.P([

    "The following websites/APIs were used in order to obtain the required data to make this webpage:",

    html.Li([
        html.A("Blomsterlandet:",
               href="https://www.blomsterlandet.se", target="_blank"),
        """
        The house plants available to purchase from Blomsterlandet were obtained via
        web-scraping. In this case I extracted the latin name of each houseplant possible
        to purchase.
        """,
        html.A("You can see the script I used to do this by clicking here.",
               href="https://github.com/RMCrean/House_Plant_Recommender/blob/main/Database/generate_database.py", target="_blank"),
    ]),

    html.Li([
        html.A("Missouri Botanical Garden:",
               href="https://www.missouribotanicalgarden.org/", target="_blank"),
        """
        The database of information available on this website was used
        """
    ]),

    html.Li([
        html.A("Google's Custom Search API:",
               href="https://developers.google.com/custom-search/v1/overview", target="_blank"),
        """
        The search API was used towards two things:
        (1) to search for each plant's web link in the Missouri Botanical Garden database.
        (2) to make automated google image searches for each plant in the database
        """,
        html.A("click here to see the script I used for this",
               href="https://github.com/RMCrean/House_Plant_Recommender/blob/main/Database/get_plant_images.py",
               target="_blank"),


    ]),

    html.Li(""),

])


faq_title_5 = ""
faq_text_5 = html.P("blah")


faq_title_6 = "I Have a Comment/Suggestion/Issue"

faq_text_6 = html.P([
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
df_plotting = pd.read_sql_query("SELECT * FROM plotting", conn)

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
                    className="display-4 text-primary"),
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
        ], xs=8, sm=8, md=8, lg=8, xl=8),  # className="mr-auto"
    ], style=banner_color),


    dbc.Row([
        html.P(subtitle_text, className="lead text-primary"),
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
                className="text-center text-primary mb-4"),
            dropdown_explain_text,
            dcc.Dropdown(
                id="dropdown-plant-select", multi=True, clearable=True,
                options=plant_search_options, placeholder=placeholder_text,
                value="Plerandra elegantissima",
            ),
        ], xs=12, sm=12, md=8, lg=8, xl=6,  style={"justify-content": "left"}, className="mb-2"),

        dbc.Col(dbc.Card([], id="plant_card_p1",
                         color="primary", outline=True),
                xs=12, sm=12, md=4, lg=4, xl=3, className="mb-2"),

        dbc.Col(dbc.Card([], id="plant_card_p2",
                         color="primary", outline=True),
                xs=12, sm=12, md=6, lg=4, xl=3, className="mb-2"),

    ]),

    # Row.
    dbc.Row([
        html.Br(), html.Br(),
        dbc.Button(info_button_text, color="info",
                   id="recommend-help-button", block=True),
        dbc.Modal(
            [
                dbc.ModalHeader("Header"),
                dbc.ModalBody("This is the content of the modal"),
                dbc.ModalFooter(
                    dbc.Button(
                        "Close", id="close", className="ms-auto", n_clicks=0
                    )
                ),
            ],
            id="modal",
            is_open=False,
        ),
    ]),

    # Row4
    dbc.Row([
        html.Hr(style=hr_styles["v2"]),
    ]),

    # Row4 - Subtitle for recommendations
    dbc.Row([
        dbc.Col([
            html.H3("The Top 6 Recommendations Based on your Selected Plant(s)",
                    className="text-center text-primary mb-4"),

        ], width=12),
    ]),

    # Row5 - Options for filtering recommendations.
    dbc.Row([
        dbc.Col([

        ], width=12),
    ]),
    # Here some sliding on off buttons would be good.
    # Could do low maintenance,
    # low sunlight requirements
    # flowers
    # gives fruits.

    # Row6 - recommendations, 1st row.
    #
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

    dbc.Row([
        html.Br()
    ]),

]

# Compare each plant on a scatter plot.
comparisons_page = [
    page_banner[0],
    page_banner[1],
    html.Br(),

    # New row - dialog buttons to control the scatter plot.
    dbc.Row([
        dbc.Col([
            html.H4("See how all the different houseplants compare",
                    className="text-center"),
            # Add explanation on how taken above features to use scatter plot.

            # Move this into the graph controls
            dbc.RadioItems(
                options=[
                    {"label": "Seperate by everything!",
                     "value": "tsne_all",
                     "label_id": "tsne_all_label"},
                    {"label": "Sunlight and watering Requirements",
                     "value": "sunlight_water"},
                    {"label": "Easiest to hardest to care for",
                     "value": "care_requirements"},
                    {"label": "Possible Plant Heights and Spreads",
                     "value": "heights_spreads"},
                ],
                value="tsne_all", id="graph_radio_buttons", inline=True,
                className="text-center"
            ),
            # TODO add more here for each one.
            dbc.Tooltip("TEST", target="tsne_all_label")
        ], className="mb-2"),
    ]),

    # Row3 -
    dbc.Row([

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5(
                        ["Click on any houseplant below to investigate it in more detail!"], className="text-center"),
                    dcc.Graph(id="scatter-graph", figure={})
                ]),
            ]),
        ], xs=12, sm=12, md=12, lg=8, xl=8, className="mb-2"),

        dbc.Col([
            dbc.Card(id="scatter-info-card",
                children=[
                    dbc.CardBody([
                        html.H5("Select a houseplant and this box will become populated!",
                                className="card-title text-center"),
                        html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(
                        ), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),
                        html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(
                        ), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),
                    ]),
                ]
            ),
        ], xs=12, sm=12, md=12, lg=4, xl=4, className="mb-2"),

    ]),
]


# FAQs page...
faqs_page = [
    page_banner[0],
    page_banner[1],
    html.Br(),
    html.H4("Frequently asked questions (FAQs)",
            style={"textAlign": "center"}),
    html.Hr(style=hr_styles["v2"]),
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
    dbc.Col([
        dbc.Card([
            dbc.CardBody([
                html.H5(faq_title_6),
                html.Hr(style=hr_styles["v3"]),
                html.P(faq_text_6),
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
                   color="primary", className="me-1"),
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
        dbc.Button("Plant Details", color="primary", className="me-1"),
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
                        f"Height Range: {plant_details['heights']}"),
                    dbc.ListGroupItem(
                        f"Spread Range: {plant_details['spreads']}"),
                    dbc.ListGroupItem(f"Zones: {plant_details['zones']}"),
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

    # TODO - do some kind of explainer on each feature.
    can use: https://dash-bootstrap-components.opensource.faculty.ai/docs/components/tooltip/

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
                    f"Number {(idx + 1)}: {top_plants[idx]}", color="primary", className="card-title text-center"),
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
                               color="primary",
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
                        f"Height Range: {plant_details['heights']}"),
                    dbc.ListGroupItem(
                        f"Spread Range: {plant_details['spreads']}"),
                    dbc.ListGroupItem(f"Zones: {plant_details['zones']}"),
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
    Output("scatter-graph", "figure"),
    Input("graph_radio_buttons", "value"),
)
def gen_scatter_plot(axes_choice):
    """
    Choose the axes to show for the scatter plot based on user input.
    # TODO - split based on what can be generic....
    # TODO - text states, name + non-unique names perhaps?
    """

    if axes_choice == "tsne_all":
        x = df_plotting["all_tsne_1"]
        y = df_plotting["all_tsne_2"]

    elif axes_choice == "tsne_all":
        x = df_plotting["all_tsne_1"]
        y = df_plotting["all_tsne_2"]

    elif axes_choice == "care_requirements":
        x = df_plotting["Sunlight_jittered"]
        y = df_plotting["Watering_jittered"]

    else:
        x = df_plotting["Max_Spread_Capped_jittered"]
        y = df_plotting["Max_Height_Capped_jittered"]

    fig = go.Figure(data=go.Scatter(
        x=x, y=y, mode="markers",
        text=df_plotting["Plant_Name"],
        marker=dict(
            size=10,
            color=df_plotting["Maintenance_Ordinal"],
            colorscale='Viridis',
            showscale=True,
        )
    ))

    return fig


# Callbacks for


# Update Info card generated for the scatter graph Main info cards.
@app.callback(
    Output("scatter-info-card", "children"),
    Input("scatter-graph", "clickData"),
    prevent_initial_call=True  # because I am reliant on a user click.
)
def get_card(clickData):
    """Rent card callback"""
    if clickData is not None:
        plant_name = clickData["points"][0]["text"]

        plant_details = utils.get_plant_details(
            plant_name=plant_name, plant_df=plant_df, image_df=image_df)

        card_content = [
        ]

    return card_content


################## End of app ##################
if __name__ == "__main__":
    app.run_server(debug=True)
