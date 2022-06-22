import os
from pathlib import Path

import numpy as np
import pandas as pd

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State

app = dash.Dash(__name__)

# files and folders
data_dir = Path('indicators')
input_folder = 'Inputs'
target_folder = 'Targets'
input_dir = data_dir/input_folder
target_dir = data_dir/target_folder
input_file_ls = [x[:-4] for x in os.listdir(input_dir) if x[-4:]=='.csv']
target_file_ls = [x[:-4] for x in os.listdir(target_dir) if x[-4:]=='.csv']

# Dropdowns
make_options = lambda ls: [{'label': x, 'value': x} for x in ls]
folder_options = make_options([input_folder, target_folder])
sort_options = make_options(['Correlation', 'Alphanumeric'])

# DataFrames
target_df = pd.DataFrame()
input_df = pd.DataFrame()
inputs_corr = pd.Series() # made again in all functions for now
target_columns = []
input_columns = []

# This is for showing country names instead of country iso3 code.
# Set to False because country_df was not approved.
country_df_allowed = False

if country_df_allowed:
    # country metadata
    country_df = pd.read_csv(data_dir/'countries.csv')
    afr_country_df = country_df[country_df['region']=='Africa']
    africa_a3 = afr_country_df['alpha-3'].values


# app layout
app.layout = html.Div([
    html.H1("Gender Based Violence (GBV) Dashboard", style={'text-align': 'center', 'margin': '5px'}),
    
    html.Div(id='top_menu', 
        style={'display':'block'},
        children=[
            html.Div(id='input_div',
                style={
                    #'background': 'red',
                    'width': '35%',
                    'display': 'inline-block',
                    'padding': '10px'
                    },
                children=[
                    html.Div(
                        style={'display': 'inline'},
                        children=[
                            html.Big('Input Folder', style={'display': 'inline'}),
                            dcc.Dropdown(
                                id='input_folder',
                                options=folder_options,
                                #multi=False,
                                value=input_folder,
                                #style={}
                            )
                        ]
                    ),
                    html.Br(),
                    html.Div(
                        style={'display': 'inline'},
                        children=[
                            html.Big('Input File', style={'display': 'inline'}),
                            dcc.Dropdown(
                                id='input_file',
                                options=[],
                                #multi=False,
                                #value='',
                                #style={}
                            )
                        ]
                    ),
                    html.Br(),
                    html.Div(
                        style={'display': 'inline'},
                        children=[
                            html.Big('Input Indicator', style={'display': 'inline'}),
                            dcc.Dropdown(
                                id='input_indicator',
                                #options=folder_options,
                                #multi=False,
                                #value=input_folder,
                                #placeholder='Hi',
                                #style={}
                            )
                        ]
                    )
                ]),
            html.Div(id='sort_div',
                style={
                    #'background': 'blue',
                    'width': '20%',
                    'display':'inline-block',
                    'padding': '10px'
                    },
                children=[
                    html.Div(
                        style={'display': 'inline'},
                        children=[
                            html.Big('Sort by', style={'display': 'inline'}),
                            dcc.Dropdown(
                                id='sort_by',
                                options=sort_options,
                                #multi=False,
                                value='Correlation',
                                #style={}
                            )
                        ]
                    ),
                ]),
            html.Div(id='output_div',
                style={
                    #'background': 'yellow',
                    'width': '35%',
                    'display':'inline-block',
                    'padding': '10px'
                    },
                children=[
                    html.Div(
                        style={'display': 'inline'},
                        children=[
                            html.Big('Target Folder', style={'display': 'inline'}),
                            dcc.Dropdown(
                                id='target_folder',
                                options=folder_options,
                                #multi=False,
                                value=target_folder,
                                #style={}
                            )
                        ]
                    ),
                    html.Br(),
                    html.Div(
                        style={'display': 'inline'},
                        children=[
                            html.Big('Target File', style={'display': 'inline'}),
                            dcc.Dropdown(
                                id='target_file',
                                options=make_options(target_file_ls),
                                #multi=False,
                                #value=input_folder,
                                #style={}
                            )
                        ]
                    ),
                    html.Br(),
                    html.Div(
                        style={'display': 'inline'},
                        children=[
                            html.Big('Target Indicator', style={'display': 'inline'}),
                            dcc.Dropdown(
                                id='target_indicator',
                                #options=folder_options,
                                #multi=False,
                                #value=input_folder,
                                #style={}
                            )
                        ]
                    )
                ])
        ]),
    
    html.Div(id='details',
        style={'display': 'block'},
        children=[
            html.H4(id='input_details', style={'margin': '2px', 'text-align': 'left', 'width':'36%', 'display': 'inline-block', 'font-weight': 'normal'}),
            html.H4(id='corr_details', style={'margin': '2px', 'text-align': 'center', 'width':'20%', 'display': 'inline-block', 'font-weight': 'normal'}),
            html.H4(id='target_details', style={'margin': '2px', 'text-align': 'right', 'width':'36%', 'display': 'inline-block', 'font-weight': 'normal'}),
        ]),
    
    html.Div(id='figures',
        style={'display':'block', 'margin': '0px'},
        children=[
            html.Div(
                style={
                    #'background': 'yellow',
                    'width': '45%',
                    'display':'inline-block',
                    'padding': '10px'
                    },
                children=[
                    dcc.Graph(id='country_fig'),
                    dcc.RadioItems(id='country_radio',
                        options=make_options(['Input', 'Target']),
                        value='Input', style={'text-align': 'center'}),
                    ]),
            html.Div(
                style={
                    #'background': 'yellow',
                    'width': '45%',
                    'display':'inline-block',
                    'padding': '10px'
                    },
                children=[
                    dcc.Graph(id='scatter_fig'),
                    ])
        ])
])


@app.callback(
    [Output(component_id='target_file', component_property='options'),
     Output(component_id='target_file', component_property='value')],
    [Input(component_id='target_folder', component_property='value')]
)
def update_target_file(folder):
    file_ls = [x[:-4] for x in os.listdir(data_dir/folder) if x[-4:]=='.csv']
    options = make_options(file_ls)
    return options, file_ls[0]

@app.callback(
    [Output(component_id='input_file', component_property='options'),
     Output(component_id='input_file', component_property='value')],
    [Input(component_id='input_folder', component_property='value')]
)
def update_input_file(folder):
    file_ls = [x[:-4] for x in os.listdir(data_dir/folder) if x[-4:]=='.csv']
    options = make_options(file_ls)
    return options, file_ls[0]


@app.callback(
    Output('target_indicator', 'options'),
    Input('target_file', 'value'),
    State('target_folder', 'value'))
def update_target_indicator(file, folder):
    global target_df, target_columns
    target_df = pd.read_csv(data_dir/folder/f'{file}.csv', index_col='Country')
    target_columns = [x for x in target_df.columns if not x.startswith('[YEAR]')]
    return make_options(target_columns)

@app.callback(
    Output('input_indicator', 'options'),
    Input('input_file', 'value'),
    Input('sort_by', 'value'),
    Input('target_indicator', 'value'),
    State('input_folder', 'value'),
    )
def update_input_indicator(file, sort_by, target_indicator, folder):
    global input_df, input_columns
    input_df = pd.read_csv(data_dir/folder/f'{file}.csv', index_col='Country')
    input_columns = [x for x in input_df.columns if not x.startswith('[YEAR]')]

    if sort_by=='Correlation':
        if target_indicator:
            inputs_corr = input_df[input_columns].corrwith(target_df[target_indicator])
            abs_corr = inputs_corr.abs().sort_values(ascending=False)
            columns = list(abs_corr.index)
        else:
            columns = input_columns
    elif sort_by=='Alphanumeric':
        columns = sorted(input_columns)

    return make_options(columns)
    

@app.callback(
    Output('country_fig', 'figure'),
    Output('scatter_fig', 'figure'),
    Output('input_details', 'children'),
    Output('corr_details', 'children'),
    Output('target_details', 'children'),
    Input('input_indicator', 'value'),
    Input('target_indicator', 'value'),
    Input('country_radio', 'value'),
    State('input_file', 'value'),
    State('target_file', 'value'))
def update_dashboard(input_indicator, target_indicator, country_radio, input_file, target_file):
    #global inputs_corr
    inputs_corr = input_df[input_columns].corrwith(target_df[target_indicator])
    df = input_df[[input_indicator]].join(target_df[[target_indicator]], on='Country',
                                      how='outer')
    hover_data = [input_indicator, target_indicator]
    
    # Add indicator years
    input_indicator_year = f"[YEAR] {input_indicator}"
    target_indicator_year = f"[YEAR] {target_indicator}"
    if input_indicator_year in input_df.columns:
        df = df.join(input_df[[input_indicator_year]], on='Country', how='left')
        hover_data.append(input_indicator_year)
    if target_indicator_year in target_df.columns:
        df = df.join(target_df[[target_indicator_year]], on='Country', how='left')
        hover_data.append(target_indicator_year)

    labels = {input_indicator: 'Input', target_indicator: 'Target',
              input_indicator_year: 'Input Year', target_indicator_year: 'Target Year'}
    
    if country_df_allowed:
        locations = df.index.map(lambda x: afr_country_df[afr_country_df['alpha-3'] == x]['name'].squeeze())
        locationmode = 'country names'
    else:
        locations = df.index
        locationmode = 'ISO-3'
    
    color = input_indicator if country_radio=='Input' else target_indicator
    country_fig = px.choropleth(df, locations=locations, locationmode=locationmode,
                        color=color,
                        #facet_col=input_indicator,
                        #hover_name=locations,
                        hover_data=hover_data,
                        scope='africa',
                        labels=labels
                        )

    df2 = df.dropna()
    if country_df_allowed:
        locations2 = df2.index.map(lambda x: afr_country_df[afr_country_df['alpha-3'] == x]['name'].squeeze())
    else:
        locations2 = df2.index

    scatter_fig = px.scatter(df2, input_indicator, target_indicator, trendline='ols',
                     hover_name=locations2, hover_data=hover_data, labels=labels)

    return (country_fig, scatter_fig,
            f"{input_file}: {input_indicator}",
            f"Correlation: {inputs_corr[input_indicator]}",
            f"{target_file}: {target_indicator}",
            )
    

if __name__ == '__main__':
    app.run_server(debug=True)