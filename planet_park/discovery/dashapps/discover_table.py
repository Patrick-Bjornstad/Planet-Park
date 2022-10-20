import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
from django_plotly_dash import DjangoDash
import pandas as pd
from geopy import distance
import requests
from urllib import parse

from ..models import Park, Activity, Topic, State
from django.forms.models import model_to_dict


# DATA PREPROCESSING

# Extract state model data
state_columns = [field.name for field in State._meta.get_fields()]
state_data = []
for instance in State.objects.all():
    state_data.append(model_to_dict(instance, fields=state_columns))
state_df = pd.DataFrame.from_records(state_data)

# Extract topic model data
topic_columns = [field.name for field in Topic._meta.get_fields()]
topic_data = []
for instance in Topic.objects.all():
    topic_data.append(model_to_dict(instance, fields=topic_columns))
topic_df = pd.DataFrame.from_records(topic_data)

# Extract activity model data
activity_columns = [field.name for field in Activity._meta.get_fields()]
activity_data = []
for instance in Activity.objects.all():
    activity_data.append(model_to_dict(instance, fields=activity_columns))
activity_df = pd.DataFrame.from_records(activity_data)

# Extract park data and make default tables
park_columns = [field.name for field in Park._meta.get_fields()]
park_columns.remove('states')
park_columns.remove('topics')
park_columns.remove('activities')
park_data = []
for instance in Park.objects.all():
    park_data.append(model_to_dict(instance, fields=park_columns))
park_df_init = pd.DataFrame.from_records(park_data)
park_df = park_df_init[['name', 'code', 'latitude', 'longitude', 'url', 'address', 'min_price']]


# DEFINE DASH APP AND LAYOUT

# Define Dash app
app = DjangoDash('DiscoverTable', add_bootstrap_links=True)

# Define layout
app.layout = html.Div([

    # Filter inputs
    html.H4('Filters'),
    html.Div([
        html.Div(
            className='row',
            children=[
                html.Div(className='col-lg', children=[
                    'Topics:',
                    dcc.Dropdown(
                        id='topic-filter',
                        options=[{'label': i, 'value': j} for i, j in zip(topic_df['name'], topic_df['topic_id'])],
                        multi=True
                    )
                ]),
                html.Div(className='col-lg', children=[
                    'Activities:',
                    dcc.Dropdown(
                        id='activity-filter',
                        options=[{'label': i, 'value': j} for i, j in zip(activity_df['name'], activity_df['activity_id'])],
                        multi=True
                    )
                ]),
                html.Div(className='col-lg', children=[
                    'States:',
                    dcc.Dropdown(
                        id='state-filter',
                        options=[{'label': i, 'value': j} for i, j in zip(state_df['state_name'], state_df['state_id'])],
                        multi=True
                    )
                ])
            ]
        ),
        html.Div(
            className='row pt-2',
            children=[
                html.Div(className='col-lg-2', children=[
                    'Entry Budget:',
                    dbc.Input(
                        id='price-filter',
                        type='number',
                        min=0,
                        max=25,
                        placeholder='$0 - $25'
                    )
                ]),
                html.Div(className='col-lg-6', children=[
                    'Current Location (optional):',
                    dbc.Input(
                        id='location-input',
                        type='text',
                        placeholder='<Address>, <City> <StateAbb> <ZipCode>'
                    )
                ]),
                html.Div(className='col-lg-2', children=[]),
                html.Div(className='col-lg-2', children=[
                    '_',
                    dbc.Button(
                        id='filters-button',
                        children='Apply Filters',
                        className='w-100',
                        color='primary'
                    )
                ]),
            ]
        ),
        html.Div(
            id='address-warning',
            className='pt-2 text-danger'
        )
    ], className='container-fluid'),

    # Park data
    html.H4('Parks', className='pt-3'),
    html.Div(
        id='table-container'
    ),

    # Current table storage
    dcc.Store(
        id='stored-table',
        data=park_df.to_dict('records')
    )

])


# DASH CALLBACKS

# Repopulate stored table based on filters
@app.callback(
    [dash.dependencies.Output('stored-table', 'data'),
     dash.dependencies.Output('address-warning', 'children')],
    [dash.dependencies.Input('filters-button', 'n_clicks')],
    [dash.dependencies.State('topic-filter', 'value'),
     dash.dependencies.State('activity-filter', 'value'),
     dash.dependencies.State('state-filter', 'value'),
     dash.dependencies.State('price-filter', 'value'),
     dash.dependencies.State('location-input', 'value')],
    prevent_initial_call=True
)
def update_stored_table(clicks, topics, activities, states, price, location):
    current_queryset = Park.objects.all()
    if topics:
        for topic in topics:
            current_queryset = current_queryset.filter(topics=topic)
    if activities:
        for activity in activities:
            current_queryset = current_queryset.filter(activities=activity)
    if states:
        current_queryset = current_queryset.filter(states__in=states)
    if price or price == 0:
        current_queryset = current_queryset.filter(min_price__lte=price)
    data = []
    for instance in current_queryset:
        data.append(model_to_dict(instance, fields=park_columns))
    if current_queryset:
        df_init = pd.DataFrame.from_records(data)
        df = df_init.copy()[['name', 'code', 'latitude', 'longitude', 'url', 'address', 'min_price']]
        if not location:
            return [df.to_dict('records'), None]
        else:
            url = 'https://nominatim.openstreetmap.org/search/' + parse.quote(location) + '?format=json'
            geo_response = requests.get(url).json()
            if not geo_response:
                return [df.to_dict('records'), 'Unable to parse given address! Performing filtering as if no address supplied.']
            else:
                loc_lat = float(geo_response[0]['lat'])
                loc_long = float(geo_response[0]['lon'])
                current_loc = (loc_lat, loc_long)
                df['distance'] = 0
                for i in df.index:
                    df.loc[i, 'distance'] = round(distance.distance(current_loc, (df.loc[i, 'latitude'], df.loc[i, 'longitude'])).miles, 1)
                return [df.to_dict('records'), None]
    else:
        return [{}, None]

# Display datatable from stored table
@app.callback(
    dash.dependencies.Output('table-container', 'children'),
    [dash.dependencies.Input('stored-table', 'data')]
)
def display_park_table(stored_df):
    if stored_df:
        stored_df = pd.DataFrame.from_records(stored_df)
        if 'distance' not in stored_df.columns:
            disp_df = stored_df.copy()[['address', 'min_price']]
            disp_df.loc[:, 'park'] = '[' + stored_df.name.map(str) + '](/discovery/' + stored_df.code.map(str) + ')'
            disp_df.rename(columns={'park': 'Park', 'address': 'Address', 'min_price': 'Fee ($)'}, inplace=True)
            disp_df = disp_df[['Park', 'Address', 'Fee ($)']]
            table = dash_table.DataTable(
                id='displayed-table',
                data=disp_df.to_dict('records'),
                columns=[{'id': i, 'name': i, 'presentation': 'markdown'} if i == 'Park' else {'id': i, 'name': i} for i in disp_df.columns],
                sort_action='native',
                style_cell={'fontFamily': 'Segoe UI'},
                style_header={'fontWeight': 'bold', 'textAlign': 'center'},
                style_cell_conditional=[
                    {'if': {'column_id': 'Park'},
                    'width': '35%'},
                    {'if': {'column_id': 'Address'},
                    'width': '50%'},
                    {'if': {'column_id': 'Fee ($)'},
                    'width': '15%'},
                ],
                style_data_conditional=[
                    {'if': {'column_id': 'Park'},
                    'paddingTop': '20px', 'paddingBottom': '0px', 'paddingLeft': '10px'},
                    {'if': {'column_id': 'Address'},
                    'paddingRight': '10px'},
                    {'if': {'column_id': 'Fee ($)'},
                    'paddingRight': '10px'},
                ]
            )
        elif 'distance' in stored_df.columns:
            disp_df = stored_df.copy()[['address', 'min_price', 'distance']]
            disp_df.loc[:, 'park'] = '[' + stored_df.name.map(str) + '](/discovery/' + stored_df.code.map(str) + ')'
            disp_df.rename(columns={'park': 'Park', 'address': 'Address', 'min_price': 'Fee ($)', 'distance': 'Distance (Mi)'}, inplace=True)
            disp_df = disp_df[['Park', 'Address', 'Fee ($)', 'Distance (Mi)']]
            table = dash_table.DataTable(
                id='displayed-table',
                data=disp_df.to_dict('records'),
                columns=[{'id': i, 'name': i, 'presentation': 'markdown'} if i == 'Park' else {'id': i, 'name': i} for i in disp_df.columns],
                sort_action='native',
                style_cell={'fontFamily': 'Segoe UI'},
                style_header={'fontWeight': 'bold', 'textAlign': 'center'},
                style_cell_conditional=[
                    {'if': {'column_id': 'Park'},
                    'width': '32.5%'},
                    {'if': {'column_id': 'Address'},
                    'width': '47.5%'},
                    {'if': {'column_id': 'Fee ($)'},
                    'width': '7.5%'},
                    {'if': {'column_id': 'Distance (Mi)'},
                    'width': '12.5%'},
                ],
                style_data_conditional=[
                    {'if': {'column_id': 'Park'},
                    'paddingTop': '20px', 'paddingBottom': '0px', 'paddingLeft': '10px'},
                    {'if': {'column_id': 'Address'},
                    'paddingRight': '10px'},
                    {'if': {'column_id': 'Fee ($)'},
                    'paddingRight': '10px'},
                    {'if': {'column_id': 'Distance (Mi)'},
                    'paddingRight': '10px'},
                ]
            )
        return table
    else:
        return html.Div('No parks match your criteria!', className='pt-2 text-danger')
