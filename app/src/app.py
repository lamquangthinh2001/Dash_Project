import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta
import dash_bootstrap_components as dbc

# Generate fake data
np.random.seed(0)
dates = pd.date_range(start='2023-01-01', end='2024-12-31')
destinations = ['Auckland', 'Wellington', 'Queenstown']
data = {'Date': [], 'Destination': [], 'Tourist_Arrivals': [], 'Revenue': []}

for date in dates:
    for dest in destinations:
        data['Date'].append(date)
        data['Destination'].append(dest)
        data['Tourist_Arrivals'].append(np.random.randint(5000, 20000))
        data['Revenue'].append(np.random.randint(100000, 500000))

df = pd.DataFrame(data)

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Declare server for Heroku deployment. Needed for Procfile.
server = app.server

# Define app layout
app.layout = dbc.Container([
    html.H1("New Zealand Tourism Dashboard", className='text-center mb-4'),
    
    dbc.Row([
        dbc.Col(
            dcc.Dropdown(id='destination-dropdown',
                         options=[{'label': dest, 'value': dest} for dest in destinations],
                         value='Auckland',
                         className='mb-3'
            ),
            width=6
        ),
        dbc.Col(
            dcc.RangeSlider(
                id='date-range-slider',
                min=df['Date'].min().timestamp(),
                max=df['Date'].max().timestamp(),
                value=[df['Date'].min().timestamp(), df['Date'].max().timestamp()],
                marks={timestamp: datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d') for timestamp in np.linspace(df['Date'].min().timestamp(), df['Date'].max().timestamp(), num=10)}
            ),
            width=6
        ),
    ]),
    
    dbc.Row([
        dbc.Col(
            dcc.Graph(id='arrival-graph'),
            width=6
        ),
        dbc.Col(
            dcc.Graph(id='revenue-graph'),
            width=6
        ),
    ]),
], fluid=True)

# Define callback functions
@app.callback(
    [Output('arrival-graph', 'figure'),
     Output('revenue-graph', 'figure')],
    [Input('destination-dropdown', 'value'),
     Input('date-range-slider', 'value')]
)
def update_graph(selected_destination, date_range):
    start_date = datetime.fromtimestamp(date_range[0])
    end_date = datetime.fromtimestamp(date_range[1])
    filtered_df = df[(df['Destination'] == selected_destination) & (df['Date'] >= start_date) & (df['Date'] <= end_date)]
    
    arrival_fig = px.line(filtered_df, x='Date', y='Tourist_Arrivals', title=f'Tourist Arrivals in {selected_destination}')
    arrival_fig.update_xaxes(title_text="Date")
    arrival_fig.update_yaxes(title_text="Tourist Arrivals")
    arrival_fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))
    
    revenue_fig = px.bar(filtered_df, x='Date', y='Revenue', title=f'Revenue in {selected_destination}')
    revenue_fig.update_xaxes(title_text="Date")
    revenue_fig.update_yaxes(title_text="Revenue (USD)")
    revenue_fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))
    
    return arrival_fig, revenue_fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)