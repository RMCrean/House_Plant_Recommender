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
        dbc.themes.CERULEAN],
    # these meta_tags ensure content is scaled correctly on different devices
    # see: https://www.w3schools.com/css/css_rwd_viewport.asp for more
    meta_tags=[{"name": "viewport",
                "content": "width=device-width, initial-scale=1"}],
)


################## App layout ##################

app.layout = dbc.Container([

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

        # multi false for now...
        dbc.Col(dcc.Dropdown(id="plant_sele_dropdown", multi=False,
                             value="Type your plant in here...",
                             ),
                width=5)
    ]),


    # Row3 -
    dbc.Row([

        dbc.Col(dcc.Graph(id="scatter_plot", figure={}), width=8),

        dbc.Col(dbc.Card([
            dbc.CardImg(src="/static/images/placeholder286x180.png", top=True),
            dbc.CardBody(
                html.P("This card has an image at the top", className="card-text"))
        ]),
        ),

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


    # Row6 - Recomendations produced.
    dbc.Row([
        dbc.Col([

        ], width=12),
    ]),





], fluid=True)


##################  Callbacks ##################


################## End of app ##################
if __name__ == "__main__":
    app.run_server(debug=True)
