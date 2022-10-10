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
placeholder_text = "Monstera deliciosa is currently selected, start typing to add another plant."


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


# # test
# top_plants = utils.recommend_plant(
#     df=plant_df,
#     plants_selected="Monstera deliciosa",
#     cosine_sim=cosine_sim)

# # print(plant_df[top_plants[0]])

# print(plant_df[plant_df["Plant_Name"].isin(["Monstera deliciosa"])])


################## preprocessing data ##################


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
            html.H5("Select which plants you want to study"),
            dcc.Dropdown(
                # TODO make multi=True possible.
                id="dropdown-plant-select", multi=False, value="Monstera deliciosa",
                options=[
                    {"label": "Monstera deliciosa", "value": "Monstera deliciosa"},
                    {"label": "Aechmea ", "value": "Aechmea "}, ],
                placeholder=placeholder_text,
            ),
        ], style={"justify-content": "left"}, className="mb-2"),
    ]),


    # Row4 - Subtitle for Recomendations
    dbc.Row([
        dbc.Col([
            html.H3("Recommendations based on your selected plant",
                    className="text-center text-primary mb-4"),

        ], width=12),
    ]),

    # Row5 - Options for filtering recomendations.
    dbc.Row([
        dbc.Col([

        ], width=12),
    ]),
    # Here some sliding on off buttons would be good.
    # Could do low maintenance,
    # low sunlight requirements
    # flowers
    # gives fruits.


    # Row6 - Recomendations, 1st row.
    #
    dbc.Row([
        dbc.Col(dbc.Card([], id="recomend_card_1",
                color="primary", outline=True)),
        dbc.Col(dbc.Card([], id="recomend_card_2",
                color="primary", outline=True)),
        dbc.Col(dbc.Card([], id="recomend_card_3",
                color="primary", outline=True)),
    ]),

    # Row7 - Recomendations, 2nd row.
    dbc.Row([
        dbc.Col(dbc.Card([], id="recomend_card_4",
                color="primary", outline=True)),
        dbc.Col(dbc.Card([], id="recomend_card_5",
                color="primary", outline=True)),
        dbc.Col(dbc.Card([], id="recomend_card_6",
                color="primary", outline=True)),
    ]),


    # New row - dialog buttons to control the scatter plot.
    dbc.Row([
        dbc.Col([
            html.H4("Choose the graph axes"),
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

# Update each of the recommended cards...

@app.callback(
    Output("recomend_card_1", "children"),
    Input("dropdown-plant-select", "value"),
)
def give_recommendations(plant_selection):
    """
    Uses the cosine similarity matrix and user selected plants to
    find top 6 plants to recommend.

    """
    top_plants = utils.recommend_plant(
        df=plant_df,
        plants_selected=plant_selection,
        cosine_sim=cosine_sim)

    # later just: top_plants
    top_df = plant_df[plant_df["Plant_Name"].isin(list(top_plants[0]))]

    card_content = [
        dbc.CardHeader(top_plants[0]),
        dbc.CardImg(src=app.get_asset_url("Adenium_obesum.jpg")),
        # add link to webpage....
        # Need to move images to assets folder instead.
        dbc.CardBody(
            [
                html.H5("Card title", className="card-title"),
                html.P(
                    "This is some card content that we'll reuse",
                    className="card-text",
                ),

                dbc.ListGroup([
                    dbc.ListGroupItem("Item 1"),
                    dbc.ListGroupItem("Item 2"),
                    dbc.ListGroupItem("Item 3"),
                ], flush=True),
            ]
        ),
    ]

    return card_content


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
