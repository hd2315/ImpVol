# -*- coding: utf-8 -*-
# Import required libraries
import os
from datetime import datetime as dt

import numpy as np
import pandas as pd
import chart_studio.plotly as py 
import flask
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

import pathlib



# Setup app
app = dash.Dash(__name__)
server = app.server

#external_css = ["https://fonts.googleapis.com/css?family=Overpass:300,300i",
#                "https://cdn.rawgit.com/plotly/dash-app-stylesheets/dab6f937fd5548cebf4c6dc7e93a10ac438f5efb/dash-#technical-charting.css"]

#for css in external_css:
#    app.css.append_css({"external_url": css})

#if 'DYNO' in os.environ:
#    app.scripts.append_script({
#        'external_url': #'https://cdn.rawgit.com/chriddyp/ca0d8f02a1659981a0ea7f013a378bbd/raw/e79f3f789517deec58f41251f7dbb6bee72c44ab/plotly_ga.j#s'
#    })
    
# Tickers
tickers_ = ['cln','mSPC']
tickers = [dict(label=str(ticker), value=str(ticker))
           for ticker in tickers_]

# Make app layout
app.layout=html.Div([
        html.H2('Plot of volatility surface'),
        dcc.Dropdown(id='data_load',
                    options=[{'label':'load','value':'load'},
                            {'label':'unload','value':'unload'}],
                    value='unload'),
        dcc.Tabs(id='tabs',children=[
                dcc.Tab(label='tab_1',children=[
                    html.Div([html.H3('Time series of a point on the surface'),
                              html.Label('Range of date'),
                              dcc.DatePickerRange(
                                id='dt_range',
                                #start_date_placeholder_text='Input start date',
                                #end_date_placeholder_text='Input end date',
                                start_date=dt(2017, 1, 25).date(),
                                end_date=dt(2017, 8, 25).date(),
                                min_date_allowed=dt(2005, 12, 30),
                                max_date_allowed=dt(2020, 5, 15),
                                #initial_visible_month=dt(2020, 5, 1)
                                
                              ),
                              html.Hr(),
                              #html.Div(id='output_container_date_picker_range'),
                              
                              html.Label('Tickers chosen'),
                              dcc.Checklist(
                                    id='tickers_chosen',
                                    options=[{'label':'cln','value':'cln'},
                                             {'label':'mSPC','value':'mSPC'}],
                                    value=['cln']),
                              html.Hr(),
                              html.Label('Options'),
                              dcc.RadioItems(
                                    id='option_ticker',
                                    options = [{'label': 'C', 'value': 'C'},
                                               {'label': 'P', 'value': 'P'}],
                                    value = 'C'),
                              html.Hr(),
                              html.Label('Term'),
                              dcc.RadioItems(
                                    id='term',
                                    options = [{'label': '1W', 'value': '1W'},
                                               {'label': '2W', 'value': '2W'},
                                               {'label': '3W', 'value': '3W'},
                                               {'label': '1M', 'value': '1M'},
                                               {'label': '2M', 'value': '2M'},
                                               {'label': '3M', 'value': '3M'},
                                               {'label': '4M', 'value': '4M'},
                                               {'label': '5M', 'value': '5M'},
                                               {'label': '6M', 'value': '6M'},
                                               {'label': '9M', 'value': '9M'},
                                               {'label': '1Y', 'value': '1Y'}],
                                    value = '1M'),
                              html.Hr(),
                              html.Label('Delta'),
                              dcc.Slider(
                                    id='delta',
                                    min = 0.1,
                                    max = 0.5,
                                    value=0.2,
                                    included=True,
                                    marks={0.1:{'label':'0.1'},
                                           0.15:{'label':'0.15'},
                                           0.2:{'label':'0.2'},
                                           0.25:{'label':'0.25'},
                                           0.3:{'label':'0.3'},
                                           0.35:{'label':'0.35'},
                                           0.4:{'label':'0.4'},
                                           0.45:{'label':'0.45'},
                                           0.5:{'label':'0.5'}}
                                ),
                              
        
                              html.Hr(),
                              dcc.Graph(id='plot_ts'),
                              
                             #  Temporary hack for live dataframe caching
                             #  'hidden' set to 'loaded' triggers next callback
                              html.P(
                                    hidden='unload',
                                    id='raw_container',
                                    style={'display': 'none'}
                               ),
                              html.P(
                                    hidden='unload',
                                    id='filtered_container',
                                    style={'display': 'none'}
                                )
                                            
                              
                             
                             ])    
                    ]),
                dcc.Tab(label='tab_2')
                #dcc.Tab(label='tab_3'),
                #dcc.Tab(label='tab_4'),
                #dcc.Tab(label='tab_5')
                 
            ]),
        ],className='row')
        
@app.callback(Output('raw_container', 'hidden'),
              [Input('data_load', 'value')])
def cache_raw_data(s):
    if s=='load':
        global df
        # use relative path
        DATA_PATH = pathlib.Path(__file__).parent.joinpath("data")  # /data
        df_cln = pd.read_csv(DATA_PATH.joinpath("cln_tenor_delta.csv"),index_col=0) 
        df_cln['Instrument']='cln'
        df_sp = pd.read_csv(DATA_PATH.joinpath("sp_500_tenor_delta.csv"),index_col=0) 
        df_sp['Instrument'] ='mSPC'
        df=pd.concat([df_cln, df_sp],ignore_index=True)
        df['SurfaceTimestamp']=pd.to_datetime(df['SurfaceTimestamp'],format='%d/%m/%Y %H:%M')
        df['TradeDate']=pd.to_datetime(df['TradeDate'],format='%d/%m/%Y %H:%M')
        month_dict={'Jan':'1','Feb':'2','Mar':'3','Apr':'4','May':'5','Jun':'6','Jul':'7','Aug':'8','Sep':'9','Oct':'10','Nov':'11','Dec':'12'}
        
        df['ExpiryDate']=df['ExpiryDate'].apply(lambda x: '-'.join([x.split('-')[0],month_dict[x.split('-')[1]],x.split('-')[2]]))
        df['ExpiryDate']=pd.to_datetime(df['ExpiryDate'],format='%d-%m-%Y')
        df['SurfaceDate']=pd.to_datetime(df['SurfaceTimestamp'].apply(lambda x:dt.date(x)))
        print('Loaded raw data')
        return 'loaded'

# Cache filtered data
@app.callback(Output('filtered_container', 'hidden'),
                  [Input('raw_container', 'hidden'),
                   Input('dt_range', 'start_date'),
                   Input('dt_range','end_date'),
                   Input('tickers_chosen','value'),
                   Input('option_ticker','value'),
                   Input('term', 'value'),
                   Input('delta','value')])  # To be split
def cache_filtered_data(hidden,start_date, end_date,
                            Instruments, option,term,delta):

    if hidden=='loaded':
        print('cache-filtered',hidden)
        print(start_date, end_date,Instruments, option,term,delta)
        global filtered_df
        filtered_df=df[(df.SurfaceDate>pd.to_datetime(start_date))&(df.SurfaceDate<=pd.to_datetime(end_date))&(df.Instrument.isin(Instruments))&(df.Type==option)&(df.Delta==delta)&(df.Tenor==term)]
        print('Loaded filtered data')
        return 'loaded'


@app.callback(Output('plot_ts','figure'),
              [Input('filtered_container', 'hidden')])
def make_time_series_plot(hidden):
    if hidden=='loaded':
        print('begin plot')
        trace1={'type':'scatter',
                 'x':filtered_df['SurfaceDate'],
                 'y':filtered_df['ImpliedVol']
               },
        layout={'hovermode':'closest',
                'xaxis': {'title':'Date'},
                'yaxis': {'title':'IV'},
        }
        data=[trace1]
        figure=dict(data=data,layout=layout)
        return figure

if __name__ == '__main__':
    app.run_server(debug=True)
