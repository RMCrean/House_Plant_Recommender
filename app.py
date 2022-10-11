"""
Main Dash application.
To run locally simply do "python app.py" and visit: http://127.0.0.1:8050/ in your web browser.
"""
import json
from logging import PlaceHolder
import sqlite3
import pandas as pd
import numpy as np

import plotly.express as px
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import utils

################## Style Selection ##################

# https://hellodash.pythonanywhere.com/theme_explorer
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.MINTY],
    # these meta_tags ensure content is scaled correctly on different devices
    # see: https://www.w3schools.com/css/css_rwd_viewport.asp for more
    meta_tags=[{"name": "viewport",
                "content": "width=device-width, initial-scale=1"}],
)

banner_color = {"background-color": "#DEDEDE"}

# horizontal rule styles.
hr_styles = {"v1": {"border": "2px lightgray solid"}, "v2": {
    "border": "1px lightgray solid"}, "v3": {"border": "0.5px lightgray solid"}}


################## text blocks ##################
subtitle_text = "Because you can never have enough houseplants..."
placeholder_text = """Results for \"Plerandra elegantissima\" are currently shown,
start typing to add a plant (or plants!) of your choosing."""

dropdown_explain_text = """
The selected plants will be used to generate the recommendations shown below.
If you select two or more plants, the recommendations will be for the combination
(each plant will be equally weighted).
"""

################## load in data ##################
DATABASE_LOC = r"Database\house_plants.db"

# setup connection
conn = sqlite3.connect(DATABASE_LOC)
c = conn.cursor()


# main df of info.
plant_df = pd.read_sql_query("SELECT * FROM plant_raw_data", conn)
print(plant_df.head(3))


# For the scatter plots
df_plotting = pd.read_sql_query("SELECT * FROM plotting", conn)
# print(df_plotting.head(3))


# plant images paths.
image_df = pd.read_sql_query("SELECT * FROM plant_images", conn)
# print(image_df.head(3))

# cosine_similarity matrix.
c.execute("SELECT * FROM cosine_sim")
raw_cosine_sim = c.fetchall()
cosine_sim = np.asarray(json.loads(raw_cosine_sim[0][1]))
# print(cosine_sim)


# Finally...
c.close()


################## data preprocessing ##################

# for the search dropdown callback.

# Old version - works but can't search common names as well.
# plant_search_options = [{"label": x, "value": x}
#                         for x in list(plant_df["Plant_Name"])]

common_names = list(plant_df["Common_Names"])
common_names_fixed = [names.replace(",", ", ") for names in common_names]

# New version, allows for searching of any common name too.
# Not the prettiest presenation though.
plant_search_options = []
for plant, plant_common_names in zip(list(plant_df["Plant_Name"]), common_names_fixed):
    plant_search_options.append(
        {"label": str(plant + ", Commonly known as: " + plant_common_names),
         "value": plant}
    )


################## App layout ##################

app.layout = dbc.Container([

    dbc.Row([
        dbc.Col([
            html.H2("Houseplant Recommender",
                    className="display-4", style={'color': "tertiary"}),
        ]),

    ], style={"background-color": "primary"}),

    dbc.Row([
        html.P(subtitle_text, className="lead"),
        html.Hr(style=hr_styles["v2"]),
        html.Br(), html.Br(),
    ], style={"background-color": "secondary"}),


    # Row1 - title + FAQ + Github link.
    dbc.Row([
        dbc.Col([
            html.H1("House Plant Recommender",
                    className="text-center text-primary mb-4"),
            html.H5(subtitle_text, className="text-center text-primary mb-4")

        ], width=12),
    ]),


    # Row2 - enter plant name.
    dbc.Row([
        dbc.Col([
            html.H5("Select the plant(s) you want to Generate Recommendations from"),
            html.P(dropdown_explain_text),
            dcc.Dropdown(
                id="dropdown-plant-select", multi=True, clearable=True,
                value="Plerandra elegantissima", options=plant_search_options,
                placeholder=placeholder_text,
            ),
        ], style={"justify-content": "left"}, className="mb-2"),
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
            dbc.Card(id="rent-info-card",
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








], fluid=True)


##################  Callbacks ##################


# # dropdown-plant-select
@app.callback(
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
    # TODO - max card height as % of screen size...

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
            dbc.CardHeader(top_plants[idx],
                           className="card-title text-center"),
            dbc.CardImg(src=plant_details['image_path']),
            dbc.CardBody([
                html.P(f"Image obtained from: {plant_details['image_source']}",
                       className="card-text text-right font-italic"),
                html.P(
                    f"Commonly known as: {plant_details['common_names']}",
                    className="card-text"),
            ]),

            dbc.CardBody(
                [
                    html.H5("Plant Details", className="card-title text-center"),
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

        all_card_content.append(card_content)

    return all_card_content


#


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


# Update Main info cards.
# "rent-info-card"


################## End of app ##################
if __name__ == "__main__":
    app.run_server(debug=True)
