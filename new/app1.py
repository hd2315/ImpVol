import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
import itertools
#import data
df_cln = pd.read_csv('./cln_tenor_delta_month.csv').iloc[:,1:]
df = df_cln.copy()
#df['SurfaceTimestamp'] = pd.to_datetime(df['SurfaceTimestamp'] )
#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#external_stylesheets = ["https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css"]

app = dash.Dash(__name__)
D_value = 0.1
month_gap = 1
period = df['SurfaceTimestamp'].unique()
period = [i for i in period[0]]
#dash layout
#set delta initial value


app.layout = html.Div(children=[

    html.Div(children=''' Plot for time and delta'''),

    dcc.Graph(id='delta_plot'),

    html.Div(children=[
        html.Div(children=''' Period Selector'''),
        dcc.RangeSlider(
            id = 'year_slider',
            min = 2006,
            max = 2020,
            step = None,
            allowCross=False,
            value=[2006, 2020],
            marks = dict(zip(list(range(2006,2021)),[str(i) for i in range(2006,2021)]),
            #tooltip={'always_visible':True}
            )),

        html.P(),
        html.Div(children=''' Delta Input'''),
        html.Div(), 

        dcc.Input(id='input_delta', value=0.1, type='number'),

        html.P(),
        html.Div(children=''' Time Step Input'''),
        html.Div(), 
        dcc.Input(id='input_time_step', value=1, type='number'),

        html.P(),
        html.Div(children=''' Stock Selector'''),
        html.Div(), 
        dcc.Checklist(
            options=[
                {'label': 'CLN', 'value': 'CLN'},
                {'label': 'mSPC', 'value': 'mSPC'}
            ],
            value=['CLN',]
        ),
          

    ],
    style={"display": "inline-block", "width": " 70%",'marginLeft': 30} ),


    
    
    ],
    style={ "grid-template-columns": " 70%",'marginLeft': 50}    
)

@app.callback(
    Output('delta_plot', 'figure'),
    [Input('year_slider', 'value'),
    Input('input_delta', 'value'),
    Input('input_time_step', 'value'),
    ])    
def update_figure(selected_year, delta, time_step):
    start = selected_year[0]
    end = selected_year[1]
    D_value = delta
    #selected_index = [i[6:] for i in df['SurfaceTimestamp']]
    filtered_df =  (pd.Series([i[6:] for i in df['SurfaceTimestamp']])>str(start)) & (pd.Series([i[6:] for i in df['SurfaceTimestamp']])<str(end))
    filtered_df = df[filtered_df]

    #generate timestep
    selected_time = [i for i in itertools.takewhile(lambda x: x*time_step <= len(filtered_df), range(len(filtered_df)))]    
    filtered_df = filtered_df.iloc[selected_time,:]
    trace= []
    return {
        'data':[dict(
            x=[i[3:10] for i in filtered_df[filtered_df['Delta'] == D_value]['SurfaceTimestamp']],
            y=filtered_df[filtered_df['Delta'] == D_value]['ImpliedVol'],
            name = 'CLN at Delta = ' + str(D_value),
            mode = 'line',
            marker=dict(color='rgb(26, 118, 255)')
        )],

        'layout':dict(
            title='visualise of volitality',
            showlegend=True,
        )
    }

if __name__ == '__main__':
    app.run_server(debug=True)