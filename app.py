"""
Main Dash application.
To run locally simply do "python app.py" and visit: http://127.0.0.1:8050/ in your web browser.
"""
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State


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


################## load in data ##################
DATABASE_LOC = r"C:\Users\Rory Crean\Dropbox (lkgroup)\Backup_HardDrive\Postdoc\PyForFun\House_Plant_Recommender\Database\house_plants.db"

conn = sqlite3.connect(DATABASE_LOC)
c = conn.cursor()
plant_df = pd.read_sql_query("SELECT * FROM plant_raw_data", conn)

c.close()
print(plant_df.head(3))


plant_df["Common_Names"]
plant_df["Plant_Name"]


################## App layout ##################

app.layout = dbc.Container([

    dbc.Row([
        dbc.Col([
            html.H2("Houseplant Recommender",
                    className="display-4", style={'color': "secondary"}),
        ]),

    ], style={"background-color": "primary"}),

    dbc.Row([
        html.P("Because you can never have enough houseplants...", className="lead"),
        html.Hr(style=hr_styles["v2"]),
        html.Br(), html.Br(),
    ], style={"background-color": "secondary"}),




    # Row1 - title + FAQ + Github link.
    dbc.Row([
        dbc.Col([
            html.H1("House Plant Recommender",
                    className="text-center text-primary mb-4"),
            html.H5("Because you can never have enough houseplants...",
                    className="text-center text-primary mb-4")

        ], width=12),
    ]),


    # Row2 - enter plant name or choose graph axes.
    dbc.Row([
        dbc.Col([
            html.H5("Select a Municipality to Study in More Detail:"),
            dcc.Dropdown(
                id="dropdown-plant-select", multi=False, value="monstera deliciosa",
                placeholder="Monstera deliciosa is currently selected, start typing to change to another plant.",
            ),
        ], style={"justify-content": "left"}, className="mb-2"),
    ]),


    # New row - dialog buttons to control the scatter plot.
    dbc.Row([
        dbc.Col([
            html.H4("Choose the graph axes"),
            # TODO - add a hover over explainin what these are.
            dbc.RadioItems(
                options=[
                    {"label": "Seperate on all properties",
                     "value": "tsne_all"},
                    {"label": "TODO_1",
                     "value": "TODO_1"},
                    {"label": "TODO_2",
                     "value": "TODO_2"},
                    {"label": "TODO_3",
                     "value": "TODO_3"},
                ],
                value="tsne_all", id="graph_radio_buttons", inline=True,
                className="text-center"
            ),
        ], className="mb-2"),
    ]),



    # Row3 -
    dbc.Row([

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5(["Median Annual Rent per m", html.Sup(
                        2), " (SEK)"], className="text-center"),
                    dcc.Graph(id="scatter-graph", figure={})
                ]),
            ]),
        ], xs=12, sm=12, md=12, lg=8, xl=8, className="mb-2"),

        dbc.Col([
            dbc.Card(id="rent-info-card",
                children=[
                    dbc.CardBody([
                        html.H5("Click on any region on the Map to populate this box!",
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








    # dbc.Row([

    #     dbc.Col([
    #         dcc.Graph(id="scatter_plot", figure={}), width=8
    #     ]),

    #     dbc.Col(dbc.Card([

    #         dbc.CardImg(src="/static/images/placeholder286x180.png", top=True),
    #         dbc.CardBody(
    #             html.P("This card has an image at the top", className="card-text"))
    #     ]),
    #     ),

    # ]),

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





], fluid=True)


##################  Callbacks ##################

# Update scatter graph callback

# Update cards - need to think about how I'm gonna do that.
# card_content = [
#     dbc.CardHeader("Card header"),
#     dbc.CardBody(
#         [
#             html.H5("Card title", className="card-title"),
#             html.P(
#                 "This is some card content that we'll reuse",
#                 className="card-text",
#             ),
#         ]
#     ),
# ]

################## End of app ##################
if __name__ == "__main__":
    app.run_server(debug=True)
