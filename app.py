import plotly.graph_objects as go 
from dash import html, dcc
from utils import *
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import dash
import numpy as np

import time

df = load_overall_data()
df_deaths_sexage, df_death_grsex = load_sexage()

def unixTimeMillis(dt):
    ''' Convert datetime to unix timestamp '''
    return int(time.mktime(dt.timetuple()))

def unixToDatetime(unix):
    ''' Convert unix timestamp to datetime. '''
    return pd.to_datetime(unix,unit='s')

def get_marks():
    marks   = dict()

    temp_date = df.index.year.astype(str) + '-' + df.index.month.astype(str)
    temp_date.unique()
    for point in temp_date.unique():

            marks[unixTimeMillis(pd.to_datetime(point))] =  { 'label' : point, "style": {"transform": "rotate(60deg)",  "padding-top" : '20px'}}
    return marks

app = dash.Dash(__name__, external_stylesheets = [dbc.themes.LUX])
server = app.server

app.layout = html.Div([

                        dbc.Row([dbc.Col([
                                        html.Hr(),
                                        html.H3( "Cov-2019 Dashboard Bulgaria", style={'text-align': 'center', 'size' : 10}),
                                        html.Hr()
                                        ], width = {'size': 6, 'offset': 3 }
                                        ),
                                        html.Hr()
                        ]),
                        dbc.Row(dbc.Col([
                                        html.H6('Date Range Selection:'),
                                        html.Hr(),
                                        html.Div([
                                        dcc.RangeSlider(id = 'slider_date',
                                                        min=unixTimeMillis(df.index.min()),
                                                        max=unixTimeMillis(df.index.max()),
                                                        marks=get_marks(),
                                                        value=[unixTimeMillis(df.index.min()), unixTimeMillis(df.index.max())]
                                                        )], style = {'height' : '80px'}),
                                       
                                        html.Hr()
                                        ], width = {'size': 5, 'offset': 1 }
                                        ),
                        ),
                        dbc.Row([

                                dbc.Col([

                                            dcc.Graph(id = 'fig1', figure={})
                                ], width = {'size': 5, 'offset': 1}),

                                dbc.Col([

                                            dcc.Graph(id = 'fig2',figure={})
                                ], width = {'size': 5, 'offset': 0})
            
                        ]),

                        dbc.Row([

                                dbc.Col([

                                            dcc.Graph(id = 'fig3',figure={})
                                ], width = {'size': 5, 'offset': 1}),

                                dbc.Col([

                                            dcc.Graph(id = 'fig4',figure={})
                                ], width = {'size': 5, 'offset': 0})
            
                        ]),

                        dbc.Row([

                                dbc.Col([
                                            dcc.Graph(id = 'fig5', figure={})
                                            
                                ], width = {'size': 5, 'offset': 1}),

                                dbc.Col([

                                            dcc.Graph(id = 'fig6', figure={})
                                ], width = {'size': 5, 'offset': 0})
            
                        ])
        
    
])

#@@@ Callbacks

@app.callback(
    [Output('fig1', 'figure'),Output('fig2', 'figure'), Output('fig3', 'figure'),Output('fig4', 'figure'),Output('fig5', 'figure'), Output('fig6', 'figure'),],
    [Input("slider_date", "value")]
)
def death_hist(date_values):

    clr1 = 'blue'
    clr2 = 'red'
    clr3 = 'green'    
    
    date_values[0] = unixToDatetime(date_values[0])
    date_values[1] = unixToDatetime(date_values[1])
    fig1 = get_chart(date_values[0], date_values[1], df, ['new_cases_roll7', 'all_hospitalized'], [clr1, clr2], ['solid', 'solid'], ['New Cases', 'Hospitalized'], 'New Cases / Hospitalized')
    fig2 = get_chart(date_values[0], date_values[1], df, ['deaths_roll7', 'icu'], [clr1, clr2], ['solid', 'solid'], ['Deaths', 'ICU load'], 'Deaths / Intensive Care Units Load')
    fig3 = get_chart(date_values[0], date_values[1], df, ['perc_PCR_roll7', 'perc_AG_roll7', 'perc_tests_roll7'], [clr1, clr2, clr3], ['solid', 'solid', 'solid'], ['PCR', 'Antigen', 'All'], 'Positive Tests per Type (%)')
    fig4 = get_chart(date_values[0], date_values[1], df, ['num_PCR_roll7', 'num_AG_roll7'], [clr1, clr2], ['solid', 'solid'], ['PCR', 'Antigen'], 'Total Number of Test per Type')
    fig5= get_age_hist(date_values[0], date_values[1],df_deaths_sexage,[clr1, clr2])
    fig6 = get_chart(date_values[0], date_values[1], df_death_grsex, ['deaths_male_roll7', 'deaths_female_roll7'], [clr1, clr2], ['solid', 'solid'], ['Male Deaths', 'Felame Deaths'], 'Male/Female Deaths')

    return fig1, fig2, fig3, fig4, fig5,  fig6



#debug=True, use_reloader=False,
app.run_server( host="0.0.0.0", port=8080)